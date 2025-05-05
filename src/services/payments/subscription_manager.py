from typing import Dict, Optional
from datetime import datetime
import logging
from src.database.db_manager import DatabaseManager

class SubscriptionManager:
    def __init__(self, db_manager: DatabaseManager):
        """Initialize subscription manager."""
        self.db = db_manager
        self.logger = logging.getLogger("subscription_manager")

    async def handle_subscription_updated(self, subscription_data: Dict, user_id: int) -> bool:
        """Handle subscription update events."""
        try:
            # Add user_id to subscription data
            subscription_data["user_id"] = user_id
            
            # Store/update the subscription in database
            self.db.store_subscription(subscription_data)
            
            return True
        except Exception as e:
            self.logger.error(f"Error handling subscription update: {str(e)}")
            return False

    async def handle_subscription_ended(self, subscription_data: Dict, user_id: int) -> bool:
        """Handle subscription end events."""
        try:
            subscription_data["user_id"] = user_id
            self.db.store_subscription(subscription_data)
            
            # Update premium status
            if subscription_data["status"] in ["canceled", "ended"]:
                self.db.update_premium_status(user_id, {
                    "tier": "free",
                    "active": True,
                    "summaries_limit": 3,
                    "summaries_used": 0
                })
            
            return True
        except Exception as e:
            self.logger.error(f"Error handling subscription end: {str(e)}")
            return False

    async def activate_subscription(
        self, 
        user_id: int, 
        tier: str, 
        subscription_data: Dict
    ) -> bool:
        """Activate subscription features for user."""
        try:
            premium_data = {
                "tier": tier,
                "active": True,
                "summaries_limit": -1 if tier == "pro" else 100,
                "summaries_used": 0,
                "activation_date": datetime.now().isoformat(),
                "expiry_date": datetime.fromtimestamp(
                    subscription_data["current_period_end"]
                ).isoformat()
            }
            
            self.db.update_premium_status(user_id, premium_data)
            return True
        except Exception as e:
            self.logger.error(f"Error activating subscription: {str(e)}")
            return False
