"""
Bot handlers package.

Bot command and callback handlers.
"""

from .basic import (
    start,
    button_callback,
)

from .limits import check_summary_limits_and_notify
from .language import handle_menu_language, handle_preferences_language, language_menu_command
from .account import handle_account

from .premium import (
    handle_premium,
    handle_support_menu,
    handle_payment_creation,
    handle_cancel_subscription_confirm,
    handle_cancel_subscription,
    handle_payment_method_selection
)
from .menu import (
    help_command,
    about_command,
    menu_command,
)

from .preferences import (
    handle_preferences,
    handle_summary_language,
    handle_audio_settings,
    handle_length_setting,
)

from .audio import handle_audio_summary

__all__ = [
    # Command handlers
    "start",
    "menu_command",
    "help_command",
    "about_command",
    "language_menu_command",
    "button_callback",
    # Module handlers
    "handle_account",
    "handle_preferences",
    "handle_summary_language",
    "handle_audio_settings",
    "handle_length_setting",
    "handle_premium",
    "handle_audio_summary",
    # Premium handlers
    "handle_support_menu",
    "handle_payment_creation",
    "handle_cancel_subscription_confirm",
    "handle_cancel_subscription",
    "handle_menu_language",
    "handle_preferences_language",
    "handle_payment_method_selection",
    "check_summary_limits_and_notify",
]
