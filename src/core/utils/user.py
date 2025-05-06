"""User-related utility functions."""

from typing import Dict
from telegram.ext import ContextTypes
from src.database.db_manager import db_manager


def get_user_preferences(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> dict:
    """Get user preferences from database."""
    try:
        return db_manager.get_user_preferences(user_id)
    except Exception as e:
        return {"language": "en", "summary_length": "medium"}


def get_user_language(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> str:
    """Get user's current language preference from database."""
    try:
        return db_manager.get_user_language(user_id)
    except Exception as e:
        return "en"
