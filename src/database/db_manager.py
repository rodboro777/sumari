import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, List, Optional
from datetime import datetime
import time
import warnings

from src.logging import metrics_collector
import logging

# Suppress specific Firestore warnings about query syntax
warnings.filterwarnings(
    "ignore", category=UserWarning, module="google.cloud.firestore_v1.base_collection"
)
logger = logging.getLogger(__name__)


class DatabaseManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize Firestore client."""
        if self._initialized:
            return

        try:
            # Try to initialize with service account file if not already initialized
            if not firebase_admin._apps:
                cred = credentials.Certificate(
                    "sumari-e218a-firebase-adminsdk-fbsvc-4237ee8346.json"
                )
                firebase_admin.initialize_app(cred)
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            raise

        self.db = firestore.client()
        self.metrics = metrics_collector
        self._initialized = True

    def _track_firestore_operation(
        self,
        operation_type: str,
        collection: str,
        doc_count: int = 1,
        success: bool = True,
        error: str = None,
    ):
        """Track Firestore operation metrics."""
        try:
            # Temporarily disabled Cloud Monitoring logging
            pass
        except Exception as e:
            self.logger.error(f"Error logging metric to Cloud Monitoring: {str(e)}")
            pass

    # User Management (minimal, just for tracking)
    def add_user(self, user_id: int) -> None:
        """Add a new user or update last seen."""
        start_time = time.time()
        try:
            user_ref = self.db.collection("users").document(str(user_id))
            user_doc = user_ref.get()
            self._track_firestore_operation("read", "users", start_time=start_time)

            if not user_doc.exists:
                # Only set default data for new users
                default_data = {
                    "user_id": user_id,
                    "created_at": firestore.SERVER_TIMESTAMP,
                    "last_seen": firestore.SERVER_TIMESTAMP,
                    "preferences": {
                        "menu_language": "en",  # Default menu language
                        "summary_length": "medium",  # Default summary length
                        "summary_language": "en",  # Default summary language
                        "audio_enabled": False,  # Default audio setting
                        "voice_gender": "female",  # Default voice gender
                        "voice_language": "en",  # Default voice language
                    },
                    "stats": {
                        "daily": {
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "summaries_used": 0,
                            "audio_summaries": 0,
                            "total_processing_time": 0,
                        },
                        "total": {
                            "summaries_used": 0,
                            "audio_summaries": 0,
                            "total_processing_time": 0,
                        },
                    },
                    "premium": {
                        "tier": "free",
                        "active": True,
                        "activation_date": datetime.now().isoformat(),
                        "expiry_date": None,
                        "summaries_limit": 3,  # 3 summaries per day for free tier
                        "summaries_used": 0,
                    },
                }
                user_ref.set(default_data)
                self._track_firestore_operation("write", "users", start_time=start_time)
            else:
                # For existing users, only update last_seen and ensure required fields exist
                user_data = user_doc.to_dict()

                # Update fields that should always be present but don't overwrite existing values
                update_data = {
                    "last_seen": firestore.SERVER_TIMESTAMP,
                    "preferences": user_data.get(
                        "preferences",
                        {
                            "menu_language": "en",
                            "summary_length": "medium",
                            "summary_language": "en",
                            "audio_enabled": False,
                            "voice_gender": "female",
                            "voice_language": "en",
                        },
                    ),
                    "stats": user_data.get(
                        "stats",
                        {
                            "daily": {
                                "date": datetime.now().strftime("%Y-%m-%d"),
                                "summaries_used": 0,
                                "audio_summaries": 0,
                                "total_processing_time": 0,
                            },
                            "total": {
                                "summaries_used": 0,
                                "audio_summaries": 0,
                                "total_processing_time": 0,
                            },
                        },
                    ),
                }

                # Only set premium data if it doesn't exist
                if "premium" not in user_data:
                    update_data["premium"] = {
                        "tier": "free",
                        "active": True,
                        "activation_date": datetime.now().isoformat(),
                        "expiry_date": None,
                        "summaries_limit": 3,
                        "summaries_used": 0,
                    }

                user_ref.set(update_data, merge=True)
                self._track_firestore_operation("write", "users", start_time=start_time)
        except Exception as e:
            self._track_firestore_operation(
                "read", "users", success=False, start_time=start_time
            )
            self.logger.error(f"Error adding/updating user: {e}")
            raise

    def update_user_activity(self, user_id: int) -> None:
        """Update user's last activity timestamp."""
        user_ref = self.db.collection("users").document(str(user_id))
        user_ref.update({"last_seen": firestore.SERVER_TIMESTAMP})

    def _reset_daily_stats_if_needed(self, user_ref) -> None:
        """Reset daily stats if it's a new day."""
        today = datetime.now().strftime("%Y-%m-%d")
        user_data = user_ref.get().to_dict()
        if (
            not user_data
            or not user_data.get("stats", {}).get("daily", {}).get("date") == today
        ):
            user_ref.update(
                {
                    "stats.daily": {
                        "date": today,
                        "summaries_used": 0,
                        "audio_summaries": 0,
                        "total_processing_time": 0,
                    }
                }
            )

    # Summary History Management
    def add_to_history(self, user_id: int, video_data: Dict) -> None:
        """Add a summary to user's history."""
        history_ref = (
            self.db.collection("users")
            .document(str(user_id))
            .collection("history")
            .document()
        )

        video_data["created_at"] = firestore.SERVER_TIMESTAMP
        history_ref.set(video_data)

        # Maintain history size limit
        self._cleanup_old_history(user_id)

    def get_user_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's summary history."""
        history_ref = (
            self.db.collection("users")
            .document(str(user_id))
            .collection("history")
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )

        history = []
        for doc in history_ref.stream():
            data = doc.to_dict()
            data["id"] = doc.id
            history.append(data)

        return history

    def _cleanup_old_history(self, user_id: int, max_size: int = 10) -> None:
        """Remove old history entries if exceeding max_size."""
        history_ref = (
            self.db.collection("users")
            .document(str(user_id))
            .collection("history")
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .offset(max_size)
        )

        docs = history_ref.stream()
        for doc in docs:
            doc.reference.delete()

    # Usage Statistics
    def log_api_usage(
        self, user_id: int, api_name: str, status: str, details: Dict = None
    ) -> None:
        """Log API usage statistics directly to user document."""
        user_ref = self.db.collection("users").document(str(user_id))

        # Reset daily stats if needed
        self._reset_daily_stats_if_needed(user_ref)

        # Update usage statistics
        if status == "success":
            processing_time = details.get("processing_time", 0) if details else 0
            is_audio = details.get("is_audio", False) if details else False

            updates = {
                "stats.total.summaries_used": firestore.Increment(1),
                "stats.total.total_processing_time": firestore.Increment(
                    processing_time
                ),
                "stats.daily.summaries_used": firestore.Increment(1),
                "stats.daily.total_processing_time": firestore.Increment(
                    processing_time
                ),
            }

            if is_audio:
                updates.update(
                    {
                        "stats.total.audio_summaries": firestore.Increment(1),
                        "stats.daily.audio_summaries": firestore.Increment(1),
                    }
                )

            user_ref.update(updates)
            self._track_firestore_operation("write", "users")

    def get_user_usage_stats(self, user_id: int, timeframe_hours: int = 24) -> Dict:
        """Get user's API usage statistics from the user document."""
        user_ref = self.db.collection("users").document(str(user_id))
        user_data = user_ref.get()
        self._track_firestore_operation("read", "users")

        if not user_data.exists:
            return {"total": 0, "success": 0, "failed": 0}

        user_dict = user_data.to_dict()
        stats = user_dict.get("stats", {})

        # If requesting 24h stats, return daily stats
        if timeframe_hours == 24:
            daily_stats = stats.get("daily", {})
            if daily_stats.get("date") != datetime.now().strftime("%Y-%m-%d"):
                return {"total": 0, "success": 0, "failed": 0}
            return {
                "total": daily_stats.get("summaries_used", 0),
                "success": daily_stats.get("summaries_used", 0),
                "failed": 0,
                "audio_summaries": daily_stats.get("audio_summaries", 0),
                "total_processing_time": daily_stats.get("total_processing_time", 0),
            }

        # Otherwise return total stats
        total_stats = stats.get("total", {})
        return {
            "total": total_stats.get("summaries_used", 0),
            "success": total_stats.get("summaries_used", 0),
            "failed": 0,
            "audio_summaries": total_stats.get("audio_summaries", 0),
            "total_processing_time": total_stats.get("total_processing_time", 0),
        }

    def get_monthly_usage(self, user_id: int) -> Dict:
        """Get user's monthly usage data."""
        try:
            user_ref = self.db.collection("users").document(str(user_id))
            user_doc = user_ref.get()

            if not user_doc.exists:
                return {
                    "summaries_used": 0,
                    "summaries_limit": 5,  # Default free tier limit
                    "tier": "free",
                }

            user_data = user_doc.to_dict()
            premium_data = user_data.get("premium", {})

            return {
                "summaries_used": premium_data.get("summaries_used", 0),
                "summaries_limit": premium_data.get("summaries_limit", 5),
                "tier": premium_data.get("tier", "free"),
            }
        except Exception as e:
            print(f"Error getting monthly usage: {e}")
            return {"summaries_used": 0, "summaries_limit": 5, "tier": "free"}

    # Error Tracking
    def log_error(
        self, error_type: str, error_message: str, user_id: Optional[int] = None
    ) -> None:
        """Log error for monitoring."""
        error_ref = self.db.collection("errors").document()
        error_data = {
            "type": error_type,
            "message": error_message,
            "user_id": user_id,
            "timestamp": firestore.SERVER_TIMESTAMP,
        }
        error_ref.set(error_data)

    # Payment Management
    def log_payment_attempt(
        self,
        user_id: int,
        tier: str,
        amount: int,
        currency: str,
        payment_type: str = "fiat",
    ) -> None:
        """Log payment attempt in database."""
        payment_ref = self.db.collection("payments").document()
        payment_data = {
            "user_id": user_id,
            "tier": tier,
            "amount": amount,
            "currency": currency,
            "payment_type": payment_type,
            "status": "pending",
            "timestamp": firestore.SERVER_TIMESTAMP,
        }
        payment_ref.set(payment_data)

    def log_successful_payment(
        self, user_id: int, tier: str, amount: int, currency: str
    ) -> None:
        """Log successful payment in database."""
        # Update latest pending payment to successful
        payments_ref = (
            self.db.collection("payments")
            .where("user_id", "==", user_id)
            .where("status", "==", "pending")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(1)
        )

        for doc in payments_ref.stream():
            doc.reference.update(
                {"status": "completed", "completed_at": firestore.SERVER_TIMESTAMP}
            )

    def update_premium_status(self, user_id: int, premium_data: Dict) -> None:
        """Update user's premium status with all necessary fields."""
        user_ref = self.db.collection("users").document(str(user_id))
        
        # Get current user data
        user_data = user_ref.get()
        if not user_data.exists:
            raise ValueError(f"User {user_id} not found in database")
            
        current_data = user_data.to_dict()
        
        # Update premium fields
        update_data = {
            "premium": {
                "tier": premium_data["tier"],
                "active": premium_data["active"],
                "expiry_date": premium_data["expiry_date"],
                "summaries_limit": premium_data.get("summaries_limit", 5),
                "subscription_id": premium_data.get("subscription_id"),
                "activation_date": firestore.SERVER_TIMESTAMP,
                "summaries_used": 0,  # Reset summaries used when upgrading
            },
            "last_seen": firestore.SERVER_TIMESTAMP,
        }
        
        # Update the document
        user_ref.set(update_data, merge=True)
        
        # Log the premium status change
        self.metrics.log_premium_status_change(
            user_id=user_id,
            old_tier=current_data.get("premium", {}).get("tier", "free"),
            new_tier=premium_data["tier"],
            active=premium_data["active"]
        )

    def get_premium_status(self, user_id: int) -> Optional[Dict]:
        """Get user's premium status."""
        user_ref = self.db.collection("users").document(str(user_id))
        user_data = user_ref.get()

        if not user_data.exists:
            return None

        user_dict = user_data.to_dict()
        return user_dict.get("premium")

    def increment_summaries_used(self, user_id: int) -> None:
        """Increment the number of summaries used by a premium user."""
        user_ref = self.db.collection("users").document(str(user_id))
        user_ref.update({"premium.summaries_used": firestore.Increment(1)})

    def update_user_preferences(self, user_id: int, preferences: Dict) -> None:
        """Update user's preferences."""
        try:
            user_ref = self.db.collection("users").document(str(user_id))
            user_ref.set({"preferences": preferences}, merge=True)
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            raise

    def get_user_preferences(self, user_id: int) -> Dict:
        """Get user's preferences."""
        try:
            user_ref = self.db.collection("users").document(str(user_id))
            user_data = user_ref.get()

            if not user_data.exists:
                return {
                    "menu_language": "en",
                    "summary_language": "en",
                    "summary_length": "medium",
                    "audio_enabled": False,
                    "voice_gender": "female",
                    "voice_language": "en",
                }

            user_dict = user_data.to_dict()
            preferences = user_dict.get("preferences", {})

            # Ensure default values if not set
            if not preferences:
                preferences = {
                    "menu_language": "en",
                    "summary_language": "en",
                    "summary_length": "medium",
                    "audio_enabled": False,
                    "voice_gender": "female",
                    "voice_language": "en",
                }

            return preferences
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {
                "menu_language": "en",
                "summary_language": "en",
                "summary_length": "medium",
                "audio_enabled": False,
                "voice_gender": "female",
                "voice_language": "en",
            }

    def get_user_data(self, user_id: int) -> Dict:
        """Get all user data including preferences and premium status."""
        user_ref = self.db.collection("users").document(str(user_id))
        user_data = user_ref.get()

        if not user_data.exists:
            return {
                "preferences": {"language": "en", "summary_length": "medium"},
                "premium": {
                    "tier": "free",
                    "active": True,
                    "summaries_limit": 3,
                    "summaries_used": 0,
                },
            }

        return user_data.to_dict()

    def update_user_language(self, user_id: int, language: str) -> None:
        """Update user's interface language preference."""
        try:
            user_ref = self.db.collection("users").document(str(user_id))
            user_ref.update({"preferences.menu_language": language})
        except Exception as e:
            self.logger.error(f"Error updating user language: {e}")
            raise

    def get_user_language(self, user_id: int) -> str:
        """Get user's interface language preference."""
        try:
            user_ref = self.db.collection("users").document(str(user_id))
            user_data = user_ref.get()
            if user_data.exists:
                preferences = user_data.to_dict().get("preferences", {})
                return preferences.get("menu_language", "en")
            return "en"  # Default to English if user not found
        except Exception as e:
            logger.error(f"Error getting user language: {e}")
            return "en"

    def count_user_summaries(
        self, user_id: int, start_date: datetime = None, end_date: datetime = None
    ) -> int:
        """
        Count the number of summaries generated by a user within a date range.

        Args:
            user_id (int): The ID of the user.
            start_date (datetime, optional): The start date of the range. Defaults to None.
            end_date (datetime, optional): The end date of the range. Defaults to None.

        Returns:
            int: The number of summaries within the specified date range.
        """
        try:
            query = self.db.collection("summaries").where("user_id", "==", user_id)

            if start_date:
                query = query.where("timestamp", ">=", start_date)
            if end_date:
                query = query.where("timestamp", "<=", end_date)

            docs = query.stream()
            return sum(1 for _ in docs)
        except Exception as e:
            logger.error(f"Error counting user summaries: {e}")
            return 0

    def store_subscription(self, subscription_data: Dict) -> None:
        """Store or update a subscription record in Firestore.

        Args:
            subscription_data: Dictionary containing subscription details from Stripe
        """
        start_time = time.time()
        try:
            sub_ref = self.db.collection("subscriptions").document(
                subscription_data["id"]
            )
            sub_ref.set(
                {
                    "subscription_id": subscription_data["id"],
                    "user_id": subscription_data["user_id"],
                    "status": subscription_data["status"],
                    "current_period_start": datetime.fromtimestamp(
                        subscription_data["current_period_start"]
                    ),
                    "current_period_end": datetime.fromtimestamp(
                        subscription_data["current_period_end"]
                    ),
                    "created_at": datetime.fromtimestamp(subscription_data["created"]),
                    "canceled_at": (
                        datetime.fromtimestamp(subscription_data["canceled_at"])
                        if subscription_data.get("canceled_at")
                        else None
                    ),
                    "ended_at": (
                        datetime.fromtimestamp(subscription_data["ended_at"])
                        if subscription_data.get("ended_at")
                        else None
                    ),
                    "product_id": subscription_data["items"]["data"][0]["price"][
                        "product"
                    ],
                    "price_id": subscription_data["items"]["data"][0]["price"]["id"],
                    "interval": subscription_data["items"]["data"][0]["price"][
                        "recurring"
                    ]["interval"],
                    "amount": subscription_data["items"]["data"][0]["price"][
                        "unit_amount"
                    ],
                    "currency": subscription_data["items"]["data"][0]["price"][
                        "currency"
                    ],
                    "payment_method": {
                        "last4": subscription_data.get("default_payment_method", {})
                        .get("card", {})
                        .get("last4"),
                        "brand": subscription_data.get("default_payment_method", {})
                        .get("card", {})
                        .get("brand"),
                    },
                },
                merge=True,
            )
            self._track_firestore_operation(
                "write", "subscriptions", start_time=start_time
            )
        except Exception as e:
            self._track_firestore_operation(
                "write", "subscriptions", success=False, start_time=start_time
            )
            logger.error(f"Error storing subscription: {e}")
            raise

    def get_user_subscription(self, user_id: int) -> Optional[Dict]:
        """Get the current active subscription for a user.

        Args:
            user_id: The user's ID

        Returns:
            Dictionary containing subscription details or None if no active subscription
        """
        start_time = time.time()
        try:
            sub_refs = (
                self.db.collection("subscriptions")
                .where("user_id", "==", user_id)
                .where("status", "in", ["active", "trialing"])
                .limit(1)
            )

            for doc in sub_refs.stream():
                self._track_firestore_operation(
                    "read", "subscriptions", start_time=start_time
                )
                return doc.to_dict()
            self._track_firestore_operation(
                "read", "subscriptions", start_time=start_time
            )
            return None

        except Exception as e:
            self._track_firestore_operation(
                "read", "subscriptions", success=False, start_time=start_time
            )
            logger.error(f"Error retrieving user subscription: {e}")
            return None

    def get_subscription_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get subscription history for a user.

        Args:
            user_id: The user's ID
            limit: Maximum number of records to return (default 10)

        Returns:
            List of subscription records
        """
        try:
            history = []
            sub_refs = (
                self.db.collection("subscriptions")
                .where("user_id", "==", user_id)
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .limit(limit)
            )

            for doc in sub_refs.stream():
                history.append(doc.to_dict())

            return history
        except Exception as e:
            logger.error(f"Error retrieving subscription history: {e}")
            return []

    def cancel_subscription(
        self, user_id: int, cancel_at_period_end: bool = True
    ) -> bool:
        """Cancel a user's subscription.

        Args:
            user_id: The user's ID
            cancel_at_period_end: If True, subscription remains active until period end.
                                If False, immediately cancels the subscription.

        Returns:
            bool: True if cancellation was successful, False otherwise
        """
        try:
            # Get current premium status
            user_ref = self.db.collection("users").document(str(user_id))
            user_doc = user_ref.get()

            if not user_doc.exists:
                return False

            premium_data = user_doc.to_dict().get("premium", {})
            current_time = datetime.now()

            # Update premium status
            premium_data.update(
                {
                    "cancelled": True,
                    "cancellation_date": current_time.isoformat(),
                    "renewable": False,  # Indicate that subscription won't auto-renew
                    "cancel_at_period_end": cancel_at_period_end,
                    # Keep other fields (tier, expiry_date, etc.) unchanged
                }
            )

            # Update in database
            user_ref.update({"premium": premium_data})

            # Update the subscription in payment provider records
            sub_ref = (
                self.db.collection("subscriptions")
                .where("user_id", "==", user_id)
                .where("status", "in", ["active", "trialing"])
                .limit(1)
            )

            for doc in sub_ref.stream():
                subscription_data = doc.to_dict()
                payment_provider = subscription_data.get("payment_provider", "stripe")

                update_data = {
                    "status": "cancelled" if not cancel_at_period_end else "active",
                    "canceled_at": current_time,
                    "cancel_at_period_end": cancel_at_period_end,
                    "renewable": False,
                }

                doc.reference.update(update_data)

                # Note: Actual payment provider API calls should be handled in payment_processor service
                # This just updates our local records

            return True

        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}", exc_info=True)
            return False


# Create a singleton instance
db_manager = DatabaseManager()
