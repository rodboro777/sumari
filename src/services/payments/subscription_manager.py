"""User subscription management."""
from typing import Dict, Optional
from datetime import datetime
import logging
from src.database import db_manager
from src.logging import metrics_collector

class SubscriptionManager:
    def __init__(self):
        """Initialize subscription manager."""
        self.db = db_manager
        self.logger = logging.getLogger("subscription_manager")
        self.metrics = metrics_collector

    async def handle_subscription_updated(self, subscription_data: Dict, user_id: int) -> bool:
        """Handle subscription update events."""
        try:
            # Add user_id to subscription data
            subscription_data["user_id"] = user_id
            
            # Get previous subscription to track tier changes
            prev_sub = self.db.get_user_subscription(user_id)
            prev_tier = prev_sub.get('tier', 'free') if prev_sub else 'free'
            new_tier = subscription_data.get('tier')
            
            # Store/update the subscription in database
            self.db.store_subscription(subscription_data)
            
            # Track tier conversion if changed
            if new_tier and prev_tier != new_tier:
                self.metrics.log_user_conversion(
                    user_id=user_id,
                    from_tier=prev_tier,
                    to_tier=new_tier,
                    source='subscription_update'
                )
            
            return True
        except Exception as e:
            self.logger.error(f"Error handling subscription update: {str(e)}")
            return False

    async def handle_subscription_ended(self, subscription_data: Dict, user_id: int) -> bool:
        """Handle subscription end events."""
        try:
            subscription_data["user_id"] = user_id
            
            # Get previous subscription to track tier changes
            prev_sub = self.db.get_user_subscription(user_id)
            prev_tier = prev_sub.get('tier') if prev_sub else None
            
            self.db.store_subscription(subscription_data)
            
            # Update premium status
            if subscription_data["status"] in ["canceled", "ended"]:
                self.db.update_premium_status(user_id, {
                    "tier": "free",
                    "active": True,
                    "summaries_limit": 3,
                    "summaries_used": 0
                })
                
                # Track conversion to free tier
                if prev_tier and prev_tier != 'free':
                    self.metrics.log_user_conversion(
                        user_id=user_id,
                        from_tier=prev_tier,
                        to_tier='free',
                        source='subscription_ended'
                    )
            
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
            # Get previous tier for conversion tracking
            prev_status = self.db.get_premium_status(user_id)
            prev_tier = prev_status.get('tier', 'free') if prev_status else 'free'
            
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
            
            # Update premium status
            self.db.update_premium_status(user_id, premium_data)
            
            # Track tier conversion
            if prev_tier != tier:
                self.metrics.log_user_conversion(
                    user_id=user_id,
                    from_tier=prev_tier,
                    to_tier=tier,
                    source='subscription_activated'
                )
            
            return True
        except Exception as e:
            self.logger.error(f"Error activating subscription: {str(e)}")
            return False

# Create a singleton instance
subscription_manager = SubscriptionManager()
