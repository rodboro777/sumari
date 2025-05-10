"""Utility functions and decorators."""

from .decorators import handle_callback_exceptions
from .video import extract_video_id, get_video_info
from .rate_limit import check_rate_limit
from .formatting import format_summary_for_telegram
from .user import (
    get_user_preferences,
    get_user_language,
    update_user_preferences,
    get_user_data,
    get_monthly_usage,
    cancel_subscription,
    get_premium_status,
    check_summary_limits,
    toggle_notifications,
    are_notifications_enabled,
)
from .text import escape_md
from .eta import calculate_eta, format_eta
from .error_handler import handle_error, format_error_message
from .language_config import LANGUAGE_OPTIONS, MENU_LANGUAGE_OPTIONS
from .audio_config import VOICE_MAP

__all__ = [
    "handle_callback_exceptions",
    "get_user_data",
    "extract_video_id",
    "get_video_info",
    "check_rate_limit",
    "format_summary_for_telegram",
    "get_user_preferences",
    "get_user_language",
    "update_user_preferences",
    "get_user_data",
    "get_monthly_usage",
    "escape_md",
    "calculate_eta",
    "format_eta",
    "handle_error",
    "format_error_message",
    "cancel_subscription",
    "get_premium_status",
    "check_summary_limits",
    "toggle_notifications",
    "are_notifications_enabled",
    "LANGUAGE_OPTIONS",
    "MENU_LANGUAGE_OPTIONS",
    "VOICE_MAP",
]
