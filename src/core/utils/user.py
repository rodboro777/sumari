"""User-related utility functions."""

from typing import Dict
from telegram.ext import ContextTypes
from src.database.db_manager import db_manager
import logging

logger = logging.getLogger(__name__)


def get_user_preferences(user_id: int) -> dict:
    """Get user preferences from database."""
    try:
        return db_manager.get_user_preferences(user_id)
    except Exception as e:
        logger.error(f"Error getting user preferences: {str(e)}")
        return {
            "language": "en",
            "summary_length": "medium",
            "notifications_enabled": True,
        }


def get_user_language(user_id: int) -> str:
    """Get user's current language preference from database."""
    try:
        return db_manager.get_user_language(user_id)
    except Exception as e:
        logger.error(f"Error getting user language: {str(e)}")
        return "en"


def update_user_preferences(user_id: int, preferences: Dict) -> None:
    """Update user preferences in database."""
    try:
        db_manager.update_user_preferences(user_id, preferences)
    except Exception as e:
        logger.error(f"Error updating user preferences: {str(e)}")


def get_user_data(user_id: int) -> dict:
    """Get user data from database."""
    try:
        return db_manager.get_user_data(user_id)
    except Exception as e:
        logger.error(f"Error getting user data: {str(e)}")
        return {"language": "en", "summary_length": "medium"}


def get_monthly_usage(user_id: int) -> dict:
    """Get user's monthly usage data from database."""
    try:
        return db_manager.get_monthly_usage(user_id)
    except Exception as e:
        logger.error(f"Error getting monthly usage: {str(e)}")
        return {"summaries_used": 0}


def get_premium_status(user_id: int) -> dict:
    """Get user's premium status from database."""
    try:
        return db_manager.get_premium_status(user_id)
    except Exception as e:
        logger.error(f"Error getting premium status: {str(e)}")
        return {"premium": False}


def cancel_subscription(user_id: int) -> None:
    """Cancel user's subscription."""
    try:
        db_manager.cancel_subscription(user_id)
    except Exception as e:
        logger.error(f"Error canceling subscription: {str(e)}")


def check_summary_limits(user_id: int) -> dict:
    """Check user's summary usage and limits.

    Returns dict with remaining summaries and limit info.
    """
    try:
        return db_manager.check_summary_limits(user_id)
    except Exception as e:
        logger.error(f"Error checking summary limits: {str(e)}")
        return {
            "remaining_summaries": 0,
            "total_limit": 5,
            "has_reached_limit": True,
            "tier": "free",
            "summaries_used": 0,
        }


def toggle_notifications(user_id: int) -> bool:
    """Toggle user's notification preference.

    Returns:
        bool: The new notification state (True for enabled, False for disabled)
    """
    try:
        preferences = get_user_preferences(user_id)
        current_state = preferences.get("notifications_enabled", True)
        preferences["notifications_enabled"] = not current_state
        update_user_preferences(user_id, preferences)
        return not current_state
    except Exception as e:
        logger.error(f"Error toggling notifications: {str(e)}")
        return True


def are_notifications_enabled(user_id: int) -> bool:
    """Check if notifications are enabled for user.

    Returns:
        bool: True if notifications are enabled, False otherwise
    """
    try:
        preferences = get_user_preferences(user_id)
        return preferences.get("notifications_enabled", True)
    except Exception as e:
        logger.error(f"Error checking notifications status: {str(e)}")
        return True
