"""Keyboard module initialization."""

from .menu import (
    create_keyboard,
    create_back_button,
    create_simple_keyboard,
    create_main_menu_keyboard,
)
from .account import create_account_keyboard
from .premium import (
    create_premium_options_keyboard,
    create_premium_upgrade_keyboard,
    create_support_menu_keyboard,
    create_subscription_cancel_keyboard,
    create_subscription_cancelled_keyboard,
)

from .payment import (
    create_payment_method_keyboard,
    create_currency_keyboard,
    create_payment_link_keyboard,
)
from .preferences import (
    create_preferences_keyboard,
    create_language_selection_keyboard,
    create_summary_length_keyboard,
)
from .voice import (
    create_voice_selection_keyboard,
    create_voice_language_keyboard,
)
from .summary import create_summary_keyboard
from .menu_language import create_menu_language_selection_keyboard

__all__ = [
    # Base keyboards
    "create_keyboard",
    "create_back_button",
    "create_simple_keyboard",
    "create_summary_keyboard",
    "create_main_menu_keyboard",
    # Account keyboards
    "create_account_keyboard",
    # Premium keyboards
    "create_premium_options_keyboard",
    "create_support_menu_keyboard",
    "create_premium_upgrade_keyboard",
    "create_subscription_cancel_keyboard",
    "create_subscription_cancelled_keyboard",
    # Payment keyboards
    "create_payment_method_keyboard",
    "create_currency_keyboard",
    "create_payment_link_keyboard",
    # Preferences keyboards
    "create_preferences_keyboard",
    "create_language_selection_keyboard",
    "create_summary_length_keyboard",
    "create_menu_language_selection_keyboard",
    # Voice keyboards
    "create_voice_selection_keyboard",
    "create_voice_language_keyboard",
]
