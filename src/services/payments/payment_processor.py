"""Payment processing service."""

from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging
from telegram import Update, LabeledPrice
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from src.services.payments.stripe_service import StripeService
from src.services.payments.nowpayments_service import NOWPaymentsService
from src.services.payments.subscription_manager import SubscriptionManager
from src.config import PAYMENT_PROVIDER_TOKEN, STRIPE_CONFIG
from src.database import db_manager
from src.logging import metrics_collector
from src.core.keyboards.payment_success import PaymentSuccessKeyboard

# Define payment provider info
PAYMENT_PROVIDERS = {
    "stripe": {"name": "Card", "enabled": True, "currencies": ["USD", "EUR", "GBP"]},
    "nowpayments": {
        "name": "Crypto",
        "enabled": True,
        "currencies": ["USDT", "BTC", "ETH"],
    },
}


class PaymentProcessor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PaymentProcessor, cls).__new__(cls)
        return cls._instance

    def __init__(self, bot=None):
        """Initialize payment processor with required services."""
        if not hasattr(self, "initialized"):
            self.logger = logging.getLogger("payment_processor")
            self.db = db_manager
            self.metrics = metrics_collector
            self.stripe = StripeService(STRIPE_CONFIG["secret_key"])
            self.nowpayments = NOWPaymentsService()
            self.subscription_manager = SubscriptionManager()
            self.premium_tiers = STRIPE_CONFIG["tiers"]
            self.payment_providers = PAYMENT_PROVIDERS
            self.initialized = True

        # Always update bot instance if provided
        if bot is not None:
            self.bot = bot
        elif not hasattr(self, "bot"):
            self.bot = None

        # TON payments configuration
        self.ton_wallets = {
            "based": "YOUR_TON_WALLET_ADDRESS_BASED",
            "pro": "YOUR_TON_WALLET_ADDRESS_PRO",
        }

    async def create_stripe_payment(
        self, tier: str, user_id: int, chat_id: int
    ) -> Tuple[bool, Dict]:
        """Create a Stripe payment session."""
        try:
            if tier not in self.premium_tiers:
                return False, {"error": "Invalid subscription tier"}

            tier_info = self.premium_tiers[tier]
            product_id = tier_info["stripe_product_id"]
            amount = tier_info["prices"]["USD"]

            if not product_id:
                return False, {
                    "error": "Stripe product ID not configured for this tier"
                }

            # Create Stripe checkout session using StripeService
            success, result = await self.stripe.create_checkout_session(
                product_id=product_id,
                user_id=user_id,
                chat_id=chat_id,
                tier=tier,
                amount=amount,
            )

            if not success:
                self.logger.error(f"Failed to create Stripe checkout session: {result}")
                return False, result

            # Log payment attempt
            self.db.log_payment_attempt(
                user_id=user_id,
                tier=tier,
                amount=amount,
                currency="USD",
                payment_type="stripe",
            )

            return True, result

        except Exception as e:
            self.logger.error(f"Error creating Stripe payment: {str(e)}")
            return False, {"error": str(e)}

    async def handle_stripe_webhook(self, event_data: Dict) -> Tuple[bool, str]:
        """Handle Stripe webhook events."""
        try:
            event_type = event_data["type"]
            event_object = event_data["data"]["object"]

            if event_type in [
                "customer.subscription.created",
                "customer.subscription.updated",
            ]:
                return await self._handle_subscription_event(event_object)

            elif event_type == "customer.subscription.deleted":
                return await self._handle_subscription_deleted(event_object)

            elif event_type == "checkout.session.completed":
                return await self._handle_checkout_completed(event_object)

            return True, "Event type not handled"

        except Exception as e:
            self.logger.error(f"Error handling Stripe webhook: {str(e)}")
            return False, str(e)

    async def _handle_subscription_event(
        self, subscription_data: Dict
    ) -> Tuple[bool, str]:
        """Handle subscription created/updated events."""
        try:
            # Get customer and user data
            customer = self.stripe.get_customer_from_subscription(
                subscription_data["id"]
            )
            if not customer:
                return False, "Could not retrieve customer data"

            user_id = int(customer["metadata"]["user_id"])
            chat_id = int(customer["metadata"]["chat_id"])

            # Get tier from product
            tier = await self._get_tier_from_subscription(subscription_data)
            if not tier:
                return False, "Invalid product ID"

            # Update user's premium status
            await self._update_premium_status(user_id, subscription_data, tier)

            # Update subscription and activate if needed
            await self.subscription_manager.handle_subscription_updated(
                subscription_data, user_id
            )

            # Activate subscription if active/trialing
            if subscription_data["status"] in ["active", "trialing"]:
                await self.subscription_manager.activate_subscription(
                    subscription_data["id"], user_id
                )

            return True, f"Subscription {subscription_data['status']} processed"

        except Exception as e:
            self.logger.error(f"Error handling subscription event: {str(e)}")
            return False, str(e)

    async def _handle_subscription_deleted(
        self, event_object: Dict
    ) -> Tuple[bool, str]:
        """Handle subscription cancellation events."""
        try:
            customer = self.stripe.get_customer_from_subscription(event_object["id"])
            if not customer:
                return False, "Could not retrieve customer data"

            user_id = int(customer["metadata"]["user_id"])
            if not user_id:
                return False, "No user_id in customer metadata"

            await self.subscription_manager.handle_subscription_ended(
                event_object, user_id
            )
            return True, "Subscription cancelled"

        except Exception as e:
            self.logger.error(f"Error handling subscription deletion: {str(e)}")
            return False, str(e)

    async def _handle_checkout_completed(self, session: Dict) -> Tuple[bool, str]:
        """Handle successful checkout session completion."""
        try:
            user_id = int(session["metadata"]["user_id"])
            chat_id = int(session["metadata"]["chat_id"])

            if user_id and chat_id:
                try:
                    # First update premium status
                    tier = session["metadata"]["tier"]
                    if tier:
                        try:
                            # Get subscription details
                            subscription_id = session.get("subscription")
                            if subscription_id:
                                subscription = self.stripe.get_subscription(
                                    subscription_id
                                )
                                self.logger.info(f"Subscription data: {subscription}")
                                current_period_end = subscription.get(
                                    "current_period_end"
                                )
                                self.logger.info(
                                    f"Current period end: {current_period_end}"
                                )

                                await self.db.update_premium_status(
                                    user_id=user_id,
                                    premium_data={
                                        "tier": tier,
                                        "active": True,
                                        "expiry_date": current_period_end,
                                        "summaries_limit": self.premium_tiers[tier][
                                            "summaries_limit"
                                        ],
                                        "subscription_id": subscription_id,
                                    },
                                )
                        except KeyError as e:
                            self.logger.error(f"Missing key in subscription data: {e}")
                            return False, f"Missing subscription data: {e}"
                        except Exception as e:
                            self.logger.error(
                                f"Error updating premium status: {str(e)}"
                            )
                            return False, str(e)

                    # Then send success message
                    user_lang = await self.db.get_user_language(chat_id)
                    language_code = user_lang or "en"
                    message = PaymentSuccessKeyboard.get_success_message(language_code)
                    keyboard = PaymentSuccessKeyboard.get_keyboard(language_code)

                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode="MarkdownV2",
                        reply_markup=keyboard,
                    )

                    return True, "Checkout session completed successfully"

                except Exception as e:
                    self.logger.error(f"Failed to send success message: {str(e)}")
                    return False, str(e)

            return False, "Missing user_id or chat_id in metadata"

        except Exception as e:
            self.logger.error(f"Error handling checkout completion: {str(e)}")
            return False, str(e)

    async def _get_tier_from_subscription(
        self, subscription_data: Dict
    ) -> Optional[str]:
        """Determine the tier based on the subscription product ID."""
        try:
            product_id = subscription_data["plan"]["product"]
            return next(
                (
                    k
                    for k, v in self.premium_tiers.items()
                    if v["stripe_product_id"] == product_id
                ),
                None,
            )
        except Exception as e:
            self.logger.error(f"Error getting tier from subscription: {str(e)}")
            return None

    async def _update_premium_status(
        self, user_id: int, subscription_data: Dict, tier: str
    ) -> None:
        """Update user's premium status in the database."""
        try:
            current_period_end = subscription_data.get("current_period_end")
            subscription_id = subscription_data.get("id")

            await self.db.update_premium_status(
                user_id=user_id,
                premium_data={
                    "tier": tier,
                    "active": True,
                    "expiry_date": current_period_end,
                    "summaries_limit": self.premium_tiers[tier]["summaries_limit"],
                    "subscription_id": subscription_id,
                },
            )
        except Exception as e:
            self.logger.error(f"Error updating premium status: {str(e)}")
            raise

    async def create_payment(
        self,
        tier: str,
        user_id: int,
        chat_id: int,
        provider: str = "stripe",
        currency: str = "USD",
    ) -> Tuple[bool, Dict]:
        """Create a payment invoice for the specified tier using the selected payment provider."""
        try:
            if tier not in self.premium_tiers:
                return False, {"error": "Invalid subscription tier"}

            tier_info = self.premium_tiers[tier]
            provider_info = self.payment_providers.get(provider)
            if not provider_info:
                return False, {"error": "Invalid payment provider"}

            # Get price from Stripe
            try:
                price_info = self.stripe.get_price_for_product(
                    tier_info["stripe_product_id"]
                )
                price = price_info["amount"]  # Amount in cents
            except Exception as e:
                self.logger.error(f"Error getting price from Stripe: {str(e)}")
                return False, {"error": "Could not fetch price information"}

            title = tier_info["name"]
            description = tier_info["description"]

            # Create invoice details
            invoice = {
                "title": f"{title} ({provider_info['name']})",
                "description": description,
                "payload": f"premium_{tier}_{user_id}_{provider}",
                "provider_token": PAYMENT_PROVIDER_TOKEN,
                "currency": currency,
                "prices": [LabeledPrice(title, price)],
            }

            # Log payment creation attempt
            self.db.log_payment_attempt(
                user_id=user_id,
                tier=tier,
                amount=price,
                currency=currency,
                payment_type=provider,
            )

            return True, invoice

        except Exception as e:
            self.logger.error(f"Error creating payment: {str(e)}")
            return False, {"error": str(e)}

    async def process_successful_payment(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> bool:
        """Handle successful payment and activate premium features."""
        try:
            payment_info = update.message.successful_payment
            payload_parts = payment_info.invoice_payload.split("_")

            if len(payload_parts) != 3:
                return False

            _, tier, user_id = payload_parts
            user_id = int(user_id)

            # Activate premium features
            await self.activate_premium(
                user_id=user_id,
                tier=tier,
                payment_amount=payment_info.total_amount,
                payment_currency=payment_info.currency,
            )

            return True

        except Exception as e:
            self.logger.error(f"Error processing payment: {str(e)}")
            return False

    async def activate_premium(
        self, user_id: int, tier: str, payment_amount: int, payment_currency: str
    ) -> None:
        """Activate premium features for the user."""
        try:
            tier_info = self.premium_tiers[tier]
            expiry_date = datetime.now() + timedelta(days=tier_info["duration_days"])

            premium_data = {
                "tier": tier,
                "active": True,
                "activation_date": datetime.now().isoformat(),
                "expiry_date": expiry_date.isoformat(),
                "summaries_limit": tier_info["summaries_limit"],
                "summaries_used": 0,
            }

            # Update user's premium status in database
            self.db.update_premium_status(user_id, premium_data)

            # Log successful payment
            self.db.log_successful_payment(
                user_id=user_id,
                tier=tier,
                amount=payment_amount,
                currency=payment_currency,
            )

        except Exception as e:
            self.logger.error(f"Error activating premium: {str(e)}")
            raise

    async def deactivate_premium(self, user_id: int) -> None:
        """Deactivate premium features for the user."""
        try:
            self.db.update_premium_status(
                user_id,
                {"active": False, "deactivation_date": datetime.now().isoformat()},
            )
        except Exception as e:
            self.logger.error(f"Error deactivating premium: {str(e)}")
            raise

    async def create_ton_payment(self, tier: str, user_id: int) -> Tuple[bool, Dict]:
        """Create a TON payment request."""
        try:
            if tier not in self.premium_tiers:
                return False, {"error": "Invalid subscription tier"}

            tier_info = self.premium_tiers[tier]
            wallet_address = self.ton_wallets[tier]

            # Create TON payment details
            payment_info = {
                "wallet_address": wallet_address,
                "amount_ton": tier_info["prices"]["USD"]
                / 100,  # Convert cents to TON equivalent
                "comment": f"premium_{tier}_{user_id}",  # Payment identification
                "tier_name": tier_info["name"],
                "description": tier_info["description"],
            }

            # Log TON payment creation attempt
            self.db.log_payment_attempt(
                user_id=user_id,
                tier=tier,
                amount=tier_info["prices"]["USD"],
                currency="TON",
                payment_type="ton",
            )

            return True, payment_info

        except Exception as e:
            self.logger.error(f"Error creating TON payment: {str(e)}")
            return False, {"error": str(e)}

    def get_available_providers(self, currency: str = None) -> Dict:
        """Get list of available payment providers, optionally filtered by currency."""
        available = {}
        for provider_id, provider in self.payment_providers.items():
            if provider["enabled"]:
                if currency is None or currency in provider["currencies"]:
                    available[provider_id] = provider
        return available

    def get_supported_currencies(self, provider: str = None) -> list:
        """Get list of supported currencies, optionally filtered by provider."""
        currencies = set()
        if provider:
            if provider in self.payment_providers:
                currencies.update(self.payment_providers[provider]["currencies"])
        else:
            for provider in self.payment_providers.values():
                if provider["enabled"]:
                    currencies.update(provider["currencies"])
        return sorted(list(currencies))

    async def handle_nowpayments_webhook(self, event_data: Dict) -> Tuple[bool, str]:
        """Handle NOWPayments webhook events."""
        try:
            payment_status = event_data.get("payment_status")
            payment_id = event_data.get("payment_id")
            order_id = event_data.get("order_id")

            if not all([payment_status, payment_id, order_id]):
                return False, "Missing required webhook data"

            # Parse order_id to get user_id and tier
            try:
                user_id, tier, _ = order_id.split("_")
                user_id = int(user_id)
            except (ValueError, AttributeError):
                return False, "Invalid order_id format"

            if payment_status == "finished":
                # Activate subscription
                await self.subscription_manager.activate_subscription(
                    user_id=user_id, tier=tier, payment_data=event_data
                )

                # Send success message
                try:
                    success_message = "🎉 Your crypto payment has been confirmed! Your subscription is now active."
                    await self.bot.send_message(chat_id=user_id, text=success_message)
                except TelegramError as e:
                    self.logger.error(f"Failed to send success message: {str(e)}")

                return True, "Payment processed successfully"

            elif payment_status in ["failed", "expired"]:
                # Handle failed payment
                try:
                    failure_message = "❌ Your crypto payment has failed or expired. Please try again."
                    await self.bot.send_message(chat_id=user_id, text=failure_message)
                except TelegramError as e:
                    self.logger.error(f"Failed to send failure message: {str(e)}")

                return True, "Payment failure handled"

            return True, f"Payment status {payment_status} not handled"

        except Exception as e:
            self.logger.error(f"Error handling NOWPayments webhook: {str(e)}")
            return False, str(e)

    async def cancel_subscription(
        self, user_id: int, cancel_at_period_end: bool = True
    ) -> Tuple[bool, str]:
        """Cancel a user's subscription.

        Args:
            user_id: The ID of the user whose subscription to cancel
            cancel_at_period_end: If True, subscription will remain active until the end of the period
                                If False, subscription will be cancelled immediately

        Returns:
            Tuple[bool, str]: Success status and result/error message
        """
        try:
            # Get user's subscription details
            subscription = self.db.get_user_subscription(user_id)
            if not subscription:
                return False, "No active subscription found"

            subscription_id = subscription.get("subscription_id")
            payment_provider = subscription.get("payment_provider", "stripe")

            # Cancel subscription with the appropriate payment provider
            if payment_provider == "stripe":
                success, result = await self.stripe.cancel_subscription(
                    subscription_id=subscription_id,
                    cancel_at_period_end=cancel_at_period_end,
                )
            elif payment_provider == "nowpayments":
                success, result = await self.nowpayments.cancel_subscription(
                    subscription_id=subscription_id,
                    cancel_at_period_end=cancel_at_period_end,
                )
            else:
                return False, f"Unsupported payment provider: {payment_provider}"

            if not success:
                return (
                    False,
                    f"Failed to cancel subscription: {result.get('error', 'Unknown error')}",
                )

            # Update subscription status in database
            self.db.cancel_subscription(
                user_id, cancel_at_period_end=cancel_at_period_end
            )

            # Log cancellation
            self.logger.info(f"Subscription cancelled for user {user_id}")
            self.metrics.log_subscription_cancelled(
                user_id=user_id,
                payment_provider=payment_provider,
                cancel_at_period_end=cancel_at_period_end,
            )

            return True, "Subscription cancelled successfully"

        except Exception as e:
            self.logger.error(f"Error cancelling subscription: {str(e)}")
            return False, str(e)


# Create singleton instance
payment_processor = PaymentProcessor()
