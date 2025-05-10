from typing import Dict, Optional, Tuple
import stripe
import logging
from datetime import datetime
from src.config import STRIPE_CONFIG


class StripeService:
    def __init__(self, stripe_secret_key: str):
        """Initialize Stripe service."""
        self.logger = logging.getLogger("stripe_service")
        stripe.api_key = stripe_secret_key
        self.prices_cache = {}
        self._initialize_prices()

    def _initialize_prices(self) -> None:
        """Initialize prices from Stripe on startup."""
        try:
            # Fetch all active prices for our products
            prices = stripe.Price.list(active=True, expand=["data.product"])

            # Organize prices by product ID
            for price in prices.data:
                if price.product:
                    self.prices_cache[price.product.id] = {
                        "amount": price.unit_amount,
                        "currency": price.currency.upper(),
                        "price_id": price.id,
                    }

            self.logger.info(f"Initialized Stripe prices: {self.prices_cache}")
        except Exception as e:
            self.logger.error(f"Error initializing Stripe prices: {str(e)}")
            raise

    def get_price_for_product(self, product_id: str) -> dict:
        """Get price information for a product.

        Args:
            product_id: Stripe product ID

        Returns:
            dict: Price information containing amount and currency
        """
        try:
            # Try to get from cache first
            if product_id in self.prices_cache:
                return self.prices_cache[product_id]

            # If not in cache, fetch from Stripe
            prices = stripe.Price.list(product=product_id, active=True, limit=1)
            if not prices.data:
                raise ValueError(f"No active price found for product {product_id}")

            price = prices.data[0]
            price_info = {
                "amount": price.unit_amount,
                "currency": price.currency.upper(),
                "price_id": price.id,
            }

            # Update cache
            self.prices_cache[product_id] = price_info
            return price_info

        except Exception as e:
            self.logger.error(f"Error getting price for product {product_id}: {str(e)}")
            raise

    async def create_checkout_session(
        self, product_id: str, user_id: int, chat_id: int, tier: str
    ) -> Tuple[bool, Dict]:
        """Create a Stripe checkout session."""
        try:
            # Get price information for the product
            price_info = self.get_price_for_product(product_id)
            if not price_info:
                return False, {"error": "No active price found for this product"}

            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_info["price_id"],
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=f"{STRIPE_CONFIG['success_url']}?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=STRIPE_CONFIG["cancel_url"],
                metadata={
                    "user_id": str(user_id),
                    "chat_id": str(chat_id),
                    "tier": tier,
                },
            )
            return True, {"session_id": session.id, "checkout_url": session.url}
        except Exception as e:
            self.logger.error(f"Error creating Stripe checkout session: {str(e)}")
            return False, {"error": str(e)}

    def get_subscription(self, subscription_id: str) -> Dict:
        """Get subscription details from Stripe."""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            # Log raw subscription data
            self.logger.info(f"Raw subscription data: {subscription}")
            # Get the subscription item data
            # Use direct access to subscription properties
            return {
                "id": subscription.id,
                "current_period_end": subscription.items.data[0].current_period_end,
                "status": subscription.status,
                "customer": subscription.customer,
            }
        except Exception as e:
            self.logger.error(f"Error retrieving subscription: {str(e)}")
            raise

    def get_customer_from_subscription(self, subscription_id: str) -> Optional[Dict]:
        """Get customer details from a subscription."""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return stripe.Customer.retrieve(subscription.customer)
        except Exception as e:
            self.logger.error(f"Error retrieving customer: {str(e)}")
            return None

    async def cancel_subscription(
        self, subscription_id: str, cancel_at_period_end: bool = True
    ) -> Tuple[bool, Dict]:
        """Cancel a Stripe subscription.

        Args:
            subscription_id: The ID of the subscription to cancel
            cancel_at_period_end: If True, subscription will remain active until the end of the period
                                If False, subscription will be cancelled immediately

        Returns:
            Tuple[bool, Dict]: Success status and result/error message
        """
        try:
            subscription = stripe.Subscription.modify(
                subscription_id, cancel_at_period_end=cancel_at_period_end
            )

            if not cancel_at_period_end:
                # Immediately cancel if requested
                subscription = stripe.Subscription.delete(subscription_id)

            return True, {"status": subscription.status}

        except Exception as e:
            self.logger.error(f"Error cancelling Stripe subscription: {str(e)}")
            return False, {"error": str(e)}
