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

    async def create_checkout_session(
        self, product_id: str, user_id: int, chat_id: int, tier: str
    ) -> Tuple[bool, Dict]:
        """Create a Stripe checkout session."""
        try:
            # First get the price ID for the product
            product = stripe.Product.retrieve(product_id)
            prices = stripe.Price.list(product=product_id, active=True, limit=1)
            if not prices.data:
                return False, {"error": "No active price found for this product"}

            price_id = prices.data[0].id

            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=f"{STRIPE_CONFIG['success_url']}?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=STRIPE_CONFIG["cancel_url"],
                metadata={
                    "user_id": str(user_id),
                    "chat_id": str(chat_id),
                    "tier": tier
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
            sub_dict = subscription.to_dict_recursive()
            return {
                "id": sub_dict["id"],
                "current_period_end": sub_dict["items"]["data"][0]["current_period_end"],
                "status": sub_dict["status"],
                "customer": sub_dict["customer"]
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
