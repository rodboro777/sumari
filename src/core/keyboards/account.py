"""Account-related keyboard layouts."""

from telegram import InlineKeyboardMarkup

from src.core.keyboards.menu import create_keyboard
from src.core.localization import get_message


def create_account_keyboard(
    language: str, has_premium: bool = False, notifications_enabled: bool = True
) -> InlineKeyboardMarkup:
    """
    Create account menu keyboard.

    Args:
        language: Language code
        has_premium: Whether the user has premium status
        notifications_enabled: Whether notifications are enabled
    """
    buttons = [
        [
            {
                "text": get_message("btn_transaction_history", language),
                "callback_data": "get_transactions",
            }
        ],
        [
            {
                "text": ("🔔 " if notifications_enabled else "🔕 ")
                + get_message("btn_notifications_on" if notifications_enabled else "btn_notifications_off", language),
                "callback_data": "toggle_notifications",
            }
        ],
    ]

    if not has_premium:
        buttons.append(
            [
                {
                    "text": get_message("btn_account_premium", language),
                    "callback_data": "premium",
                }
            ]
        )

    buttons.append(
        [
            {
                "text": get_message("btn_account_back", language),
                "callback_data": "back_to_menu",
            }
        ]
    )

    return create_keyboard(buttons, language)
