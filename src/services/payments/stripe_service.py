from typing import Dict, Optional, Tuple
import stripe
import logging
from datetime import datetime

class StripeService:
    def __init__(self, stripe_secret_key: str):
        """Initialize Stripe service."""
        self.logger = logging.getLogger("stripe_service")
        stripe.api_key = stripe_secret_key

    async def create_checkout_session(
        self, 
        product_id: str, 
        user_id: int, 
        chat_id: int
    ) -> Tuple[bool, Dict]:
        """Create a Stripe checkout session."""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card", "crypto"],
                line_items=[{
                    "product": product_id,
                    "quantity": 1,
                }],
                mode="subscription",
                success_url="https://your-domain.com/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="https://your-domain.com/cancel",
                metadata={
                    "user_id": str(user_id),
                    "chat_id": str(chat_id),
                },
            )
            return True, {"session_id": session.id, "checkout_url": session.url}
        except Exception as e:
            self.logger.error(f"Error creating Stripe checkout session: {str(e)}")
            return False, {"error": str(e)}

    def get_customer_from_subscription(self, subscription_id: str) -> Optional[Dict]:
        """Get customer details from a subscription."""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return stripe.Customer.retrieve(subscription.customer)
        except Exception as e:
            self.logger.error(f"Error retrieving customer: {str(e)}")
            return None

    def get_subscription(self, subscription_id: str) -> Optional[Dict]:
        """Get subscription details."""
        try:
            return stripe.Subscription.retrieve(subscription_id)
        except Exception as e:
            self.logger.error(f"Error retrieving subscription: {str(e)}")
            return None
