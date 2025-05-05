"""Account-related keyboard layouts."""

from typing import Dict
from telegram import InlineKeyboardMarkup

from .base import create_keyboard, ButtonData

ACCOUNT_BUTTONS = {
    "history": {
        "text": {"en": "📊 History", "ru": "📊 История"},
        "callback_data": "view_full_history",
    },
    "premium": {
        "text": {"en": "⭐ Premium", "ru": "⭐ Премиум"},
        "callback_data": "premium",
    },
    "back": {
        "text": {"en": "⬅️ Back to Menu", "ru": "⬅️ Вернуться в меню"},
        "callback_data": "back_to_menu",
    },
}


def create_account_keyboard(
    language: str, has_premium: bool = False
) -> InlineKeyboardMarkup:
    """
    Create account menu keyboard.

    Args:
        language: Language code
        has_premium: Whether the user has premium status
    """
    buttons = [[ACCOUNT_BUTTONS["history"]]]

    if not has_premium:
        buttons.append([ACCOUNT_BUTTONS["premium"]])

    buttons.append([ACCOUNT_BUTTONS["back"]])

    return create_keyboard(buttons, language)


def create_account_settings_keyboard(language: str) -> InlineKeyboardMarkup:
    """Create account settings keyboard."""
    buttons = [
        [
            {
                "text": {"en": "🔔 Notifications", "ru": "🔔 Уведомления"},
                "callback_data": "account_notifications",
            }
        ],
        [
            {
                "text": {"en": "🗑 Delete Account", "ru": "🗑 Удалить аккаунт"},
                "callback_data": "account_delete",
            }
        ],
        [ACCOUNT_BUTTONS["back"]],
    ]

    return create_keyboard(buttons, language)
