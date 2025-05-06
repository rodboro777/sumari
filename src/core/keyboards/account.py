"""Account-related keyboard layouts."""

from typing import Dict
from telegram import InlineKeyboardMarkup

from .base import create_keyboard, ButtonData
from src.core.localization import get_message

ACCOUNT_BUTTONS = {
    "history": {
        "callback_data": "view_full_history",
    },
    "premium": {
        "callback_data": "premium",
    },
    "back": {
        "callback_data": "back_to_menu",
    },
    "settings": {
        "callback_data": "account_settings",
    },
    "notifications": {
        "callback_data": "account_notifications",
    },
    "delete": {
        "callback_data": "account_delete",
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
    buttons = [
        [
            {
                "text": get_message("btn_account_history", language),
                "callback_data": ACCOUNT_BUTTONS["history"]["callback_data"],
            }
        ],
        [
            {
                "text": get_message("btn_account_settings", language),
                "callback_data": ACCOUNT_BUTTONS["settings"]["callback_data"],
            }
        ]
    ]

    if not has_premium:
        buttons.append([
            {
                "text": get_message("btn_account_premium", language),
                "callback_data": ACCOUNT_BUTTONS["premium"]["callback_data"],
            }
        ])

    buttons.append([
        {
            "text": get_message("btn_account_back", language),
            "callback_data": ACCOUNT_BUTTONS["back"]["callback_data"],
        }
    ])

    return create_keyboard(buttons, language)
