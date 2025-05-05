from typing import Dict, Optional, Tuple
from datetime import datetime
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from src.database.db_manager import DatabaseManager
from src.services.payments.stripe_service import StripeService
from src.services.payments.nowpayments_service import NOWPaymentsService
from src.services.payments.subscription_manager import SubscriptionManager

class PaymentProcessor:
    def __init__(
        self,
        db_manager: DatabaseManager,
        stripe_secret_key: str,
    ):
        """Initialize payment processor with required services."""
        self.logger = logging.getLogger("payment_processor")
        self.db = db_manager
        
        # Initialize services
        self.stripe = StripeService(stripe_secret_key)
        self.nowpayments = NOWPaymentsService()
        self.subscription_manager = SubscriptionManager(db_manager)

        # Premium tiers configuration
        self.premium_tiers = {
            "based": {
                "name": "Based Premium",
                "description": "100 summaries per month",
                "summaries_limit": 100,
                "duration_days": 30,
                "features": ["100 summaries/month", "Text summaries"],
                "stripe_product_id": "prod_SFe1nUFkkKHG5j",
            },
            "pro": {
                "name": "Pro Premium",
                "description": "Unlimited summaries + Audio versions",
                "summaries_limit": -1,  # unlimited
                "duration_days": 30,
                "features": [
                    "Unlimited summaries",
                    "Text & Audio summaries",
                    "Priority processing",
                ],
                "stripe_product_id": "prod_SFe2WqvSrS2sA7",
            },
        }

        # TON payments configuration
        self.ton_wallets = {
            "based": "YOUR_TON_WALLET_ADDRESS_BASED",
            "pro": "YOUR_TON_WALLET_ADDRESS_PRO",
        }

    async def create_stripe_payment(
        self, tier: str, user_id: int, chat_id: int, currency: str = "USD"
    ) -> Tuple[bool, Dict]:
        """Create a Stripe payment session."""
        try:
            if tier not in self.premium_tiers:
                return False, {"error": "Invalid subscription tier"}

            tier_info = self.premium_tiers[tier]
            product_id = tier_info["stripe_product_id"]

            if not product_id:
                return False, {
                    "error": f"Currency {currency} not supported for Stripe payments"
                }

            # Create Stripe checkout session using StripeService
            success, result = await self.stripe.create_checkout_session(
                product_id=product_id,
                user_id=user_id,
                chat_id=chat_id
            )

            if not success:
                return False, result

            # Log payment attempt
            self.db.log_payment_attempt(
                user_id=user_id,
                chat_id=chat_id,
                tier=tier,
                amount=tier_info["price"],
                currency=currency,
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
            
            # Handle subscription events
            if event_type in ["customer.subscription.created", "customer.subscription.updated"]:
                # Get user_id from customer metadata
                customer = self.stripe.get_customer_from_subscription(event_object["id"])
                if not customer:
                    return False, "Could not retrieve customer data"
                
                user_id = int(customer.metadata.get("user_id"))
                
                # Find tier based on product ID
                product_id = event_object["items"]["data"][0]["price"]["product"]
                # Get tier from product
                subscription = self.stripe.get_subscription(event_object["id"])
                if not subscription:
                    return False, "Could not retrieve subscription data"
                
                product_id = subscription.items.data[0].price.product
                tier = next(
                    (k for k, v in self.premium_tiers.items() 
                     if v["stripe_product_id"] == product_id),
                    None
                )
                
                if not tier:
                    return False, "Invalid product ID"
                
                # Update subscription and activate if needed
                await self.subscription_manager.handle_subscription_updated(event_object, user_id)
                if event_object["status"] in ["active", "trialing"]:
                    await self.subscription_manager.activate_subscription(user_id, tier, event_object)
                
                return True, f"Subscription {event_object['status']} processed"
                
            elif event_type == "customer.subscription.deleted":
                # Handle subscription cancellation
                customer = self.stripe.get_customer_from_subscription(event_object["id"])
                if not customer:
                    return False, "Could not retrieve customer data"
                
                user_id = int(customer.metadata.get("user_id"))
                if not user_id:
                    return False, "No user_id in customer metadata"
                
                await self.subscription_manager.handle_subscription_ended(event_object, user_id)
                return True, "Subscription cancelled"
                
            elif event_type == "checkout.session.completed":
                # Handle successful checkout
                session = event_object
                user_id = int(session["metadata"].get("user_id"))
                chat_id = int(session["metadata"].get("chat_id"))
                
                if user_id and chat_id:
                    # Send success message to user
                    success_message = "🎉 Payment successful! Your premium features are now active."
                    try:
                        await self.bot.send_message(chat_id=chat_id, text=success_message)
                    except TelegramError as e:
                        self.logger.error(f"Failed to send success message: {str(e)}")
                    
                    return True, "Checkout session completed successfully"
                
                return False, "Missing user_id or chat_id in metadata"
            
            return True, "Event type not handled"
        except Exception as e:
            self.logger.error(f"Error handling Stripe webhook: {str(e)}")
            return False, str(e)

    async def create_payment(
        self, tier: str, user_id: int, chat_id: int, provider: str = "stripe", currency: str = "USD"
    ) -> Tuple[bool, Dict]:
        """Create a payment invoice for the specified tier using the selected payment provider."""
        try:
            if tier not in self.premium_tiers:
                return False, {"error": "Invalid subscription tier"}

            tier_info = self.premium_tiers[tier]
            price = tier_info["prices"][currency]

            # Create invoice details
            invoice = {
                "title": f"{tier_info['name']} ({provider_info['name']})",
                "description": tier_info["description"],
                "payload": f"premium_{tier}_{user_id}_{provider}",
                "provider_token": self.provider_token,
                "currency": currency,
                "prices": [LabeledPrice(tier_info["name"], price)],
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

    async def check_premium_status(self, user_id: int) -> Dict:
        """Check user's premium status and remaining quota."""
        try:
            premium_data = self.db.get_premium_status(user_id)

            # Log the raw data we get from database
            self.logger.info(
                f"Raw premium data from DB for user {user_id}: {premium_data}"
            )

            # Super simple check - if no data or not active or free tier, return free tier
            if (
                not premium_data
                or not premium_data.get("active")
                or premium_data.get("tier") == "free"
            ):
                self.logger.info(
                    f"User {user_id} is on free tier. Active: {premium_data.get('active') if premium_data else None}, Tier: {premium_data.get('tier') if premium_data else None}"
                )
                return {
                    "active": True,
                    "tier": "free",
                    "summaries_limit": 3,
                    "summaries_used": (
                        premium_data.get("summaries_used", 0) if premium_data else 0
                    ),
                    "audio_used": (
                        premium_data.get("audio_used", 0) if premium_data else 0
                    ),
                    "total_processing_time": (
                        premium_data.get("total_processing_time", 0)
                        if premium_data
                        else 0
                    ),
                    "activation_date": None,
                    "expiry_date": None,
                }

            # If we get here, user has an active paid subscription
            self.logger.info(
                f"User {user_id} has active paid subscription. Tier: {premium_data.get('tier')}"
            )
            return premium_data

        except Exception as e:
            self.logger.error(
                f"Error checking premium status for user {user_id}: {str(e)}"
            )
            return {
                "active": True,
                "tier": "free",
                "summaries_limit": 3,
                "summaries_used": 0,
                "audio_used": 0,
                "total_processing_time": 0,
                "activation_date": None,
                "expiry_date": None,
            }

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
                    user_id=user_id,
                    tier=tier,
                    payment_data=event_data
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
