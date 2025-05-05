import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, List, Optional
from datetime import datetime

import warnings

# Suppress specific Firestore warnings about query syntax
warnings.filterwarnings(
    "ignore", category=UserWarning, module="google.cloud.firestore_v1.base_collection"
)


class DatabaseManager:
    def __init__(self):
        """Initialize Firestore client."""
        try:
            # Try to initialize with service account file
            cred = credentials.Certificate(
                "sumari-e218a-firebase-adminsdk-fbsvc-4237ee8346.json"
            )
            firebase_admin.initialize_app(cred)
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            raise

        self.db = firestore.client()

    # User Management (minimal, just for tracking)
    def add_user(self, user_id: int) -> None:
        """Add a new user or update last seen."""
        user_ref = self.db.collection("users").document(str(user_id))
        user_doc = user_ref.get()

        if not user_doc.exists:
            # Only set default data for new users
            default_data = {
                "user_id": user_id,
                "created_at": firestore.SERVER_TIMESTAMP,
                "last_seen": firestore.SERVER_TIMESTAMP,
                "language": "en",  # Default language
                "preferences": {
                    "summary_length": "medium",  # Default summary length
                    "summary_language": "en",  # Default summary language
                    "audio_enabled": False,  # Default audio setting
                    "voice_gender": "female",  # Default voice gender
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
        else:
            # For existing users, only update last_seen and ensure required fields exist
            # without overwriting premium status
            user_data = user_doc.to_dict()

            # Update fields that should always be present but don't overwrite existing values
            update_data = {
                "last_seen": firestore.SERVER_TIMESTAMP,
                "language": user_data.get("language", "en"),
                "preferences": user_data.get(
                    "preferences",
                    {
                        "summary_length": "medium",
                        "summary_language": "en",
                        "audio_enabled": False,
                        "voice_gender": "female",
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

    def get_user_usage_stats(self, user_id: int, timeframe_hours: int = 24) -> Dict:
        """Get user's API usage statistics from the user document."""
        user_ref = self.db.collection("users").document(str(user_id))
        user_data = user_ref.get()

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
        """Update user's premium status."""
        user_ref = self.db.collection("users").document(str(user_id))
        user_ref.set({"premium": premium_data}, merge=True)

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
                return {"language": "en", "summary_length": "medium"}

            user_dict = user_data.to_dict()
            preferences = user_dict.get("preferences", {})

            # Ensure default values if not set
            if not preferences:
                preferences = {"language": "en", "summary_length": "medium"}

            return preferences
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {"language": "en", "summary_length": "medium"}

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
            user_ref.update({"language": language})
        except Exception as e:
            logger.error(f"Error updating user language: {e}")
            raise

    def get_user_language(self, user_id: int) -> str:
        """Get user's interface language preference."""
        try:
            user_ref = self.db.collection("users").document(str(user_id))
            user_data = user_ref.get()
            if user_data.exists:
                return user_data.to_dict().get("language", "en")
            return "en"  # Default to English if user not found
        except Exception as e:
            logger.error(f"Error getting user language: {e}")
            return "en"


    def store_subscription(self, subscription_data: Dict) -> None:
        """Store or update a subscription record in Firestore.

        Args:
            subscription_data: Dictionary containing subscription details from Stripe
        """
        try:
            sub_ref = self.db.collection('subscriptions').document(subscription_data['id'])
            sub_ref.set({
                'subscription_id': subscription_data['id'],
                'user_id': subscription_data['user_id'],
                'status': subscription_data['status'],
                'current_period_start': datetime.fromtimestamp(subscription_data['current_period_start']),
                'current_period_end': datetime.fromtimestamp(subscription_data['current_period_end']),
                'created_at': datetime.fromtimestamp(subscription_data['created']),
                'canceled_at': datetime.fromtimestamp(subscription_data['canceled_at']) if subscription_data.get('canceled_at') else None,
                'ended_at': datetime.fromtimestamp(subscription_data['ended_at']) if subscription_data.get('ended_at') else None,
                'product_id': subscription_data['items']['data'][0]['price']['product'],
                'price_id': subscription_data['items']['data'][0]['price']['id'],
                'interval': subscription_data['items']['data'][0]['price']['recurring']['interval'],
                'amount': subscription_data['items']['data'][0]['price']['unit_amount'],
                'currency': subscription_data['items']['data'][0]['price']['currency'],
                'payment_method': {
                    'last4': subscription_data.get('default_payment_method', {}).get('card', {}).get('last4'),
                    'brand': subscription_data.get('default_payment_method', {}).get('card', {}).get('brand')
                }
            }, merge=True)
        except Exception as e:
            logger.error(f"Error storing subscription: {e}")
            raise

    def get_user_subscription(self, user_id: int) -> Optional[Dict]:
        """Get the current active subscription for a user.

        Args:
            user_id: The user's ID

        Returns:
            Dictionary containing subscription details or None if no active subscription
        """
        try:
            sub_refs = (
                self.db.collection('subscriptions')
                .where('user_id', '==', user_id)
                .where('status', 'in', ['active', 'trialing'])
                .limit(1)
            )

            for doc in sub_refs.stream():
                return doc.to_dict()
            return None

        except Exception as e:
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
                self.db.collection('subscriptions')
                .where('user_id', '==', user_id)
                .order_by('created_at', direction=firestore.Query.DESCENDING)
                .limit(limit)
            )

            for doc in sub_refs.stream():
                history.append(doc.to_dict())

            return history
        except Exception as e:
            logger.error(f"Error retrieving subscription history: {e}")
            return []

# Create a singleton instance
db_manager = DatabaseManager()
