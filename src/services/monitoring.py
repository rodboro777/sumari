import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
import json
from src.database.db_manager import DatabaseManager


class MonitoringService:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger("monitoring")
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging settings."""
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # File handler
        file_handler = logging.FileHandler("data/monitoring.log")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        self.logger.setLevel(logging.INFO)

    def log_user_action(
        self, user_id: int, action: str, details: Optional[Dict] = None
    ):
        """Log user actions for monitoring."""
        try:
            self.db.log_action(user_id, action, details)
            self.logger.info(f"User {user_id} performed action: {action}")
        except Exception as e:
            self.logger.error(f"Error logging user action: {str(e)}")

    def track_api_usage(self, api_name: str, success: bool, response_time: float):
        """Track API calls and their performance."""
        self.logger.info(
            f"API Call - {api_name} - Success: {success} - Response Time: {response_time:.2f}s"
        )

    def track_error(
        self, error_type: str, error_message: str, user_id: Optional[int] = None
    ):
        """Track errors that occur during bot operation."""
        error_details = {
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat(),
        }

        if user_id:
            error_details["user_id"] = user_id
            self.db.log_action(user_id, "error", error_details)

        self.logger.error(f"Error occurred: {error_type} - {error_message}")

    def get_daily_stats(self) -> Dict:
        """Get daily usage statistics."""
        try:
            with self.db.db_path as conn:
                cursor = conn.cursor()
                today = datetime.now().date()

                # Get total users
                cursor.execute(
                    """
                    SELECT COUNT(DISTINCT user_id)
                    FROM usage_stats
                    WHERE DATE(timestamp) = ?
                """,
                    (today,),
                )
                active_users = cursor.fetchone()[0]

                # Get total summaries
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM summaries
                    WHERE DATE(created_at) = ?
                """,
                    (today,),
                )
                total_summaries = cursor.fetchone()[0]

                # Get average summary length
                cursor.execute(
                    """
                    SELECT AVG(LENGTH(summary))
                    FROM summaries
                    WHERE DATE(created_at) = ?
                """,
                    (today,),
                )
                avg_summary_length = cursor.fetchone()[0] or 0

                return {
                    "date": today.isoformat(),
                    "active_users": active_users,
                    "total_summaries": total_summaries,
                    "avg_summary_length": round(avg_summary_length, 2),
                }
        except Exception as e:
            self.logger.error(f"Error getting daily stats: {str(e)}")
            return {"date": today.isoformat(), "error": str(e)}

    def check_user_activity(self, user_id: int) -> Dict:
        """Check user's activity statistics."""
        try:
            with self.db.db_path as conn:
                cursor = conn.cursor()

                # Get user's total summaries
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM summaries
                    WHERE user_id = ?
                """,
                    (user_id,),
                )
                total_summaries = cursor.fetchone()[0]

                # Get user's last active time
                cursor.execute(
                    """
                    SELECT last_active
                    FROM users
                    WHERE user_id = ?
                """,
                    (user_id,),
                )
                last_active = cursor.fetchone()[0]

                return {
                    "user_id": user_id,
                    "total_summaries": total_summaries,
                    "last_active": last_active,
                    "is_active": (
                        datetime.fromisoformat(last_active)
                        > datetime.now() - timedelta(days=7)
                        if last_active
                        else False
                    ),
                }
        except Exception as e:
            self.logger.error(f"Error checking user activity: {str(e)}")
            return {"user_id": user_id, "error": str(e)}
