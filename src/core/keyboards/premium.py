"""Premium-related keyboard layouts."""

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import logging

from src.core.localization import get_message

logger = logging.getLogger(__name__)


def create_premium_options_keyboard(
    language: str,
    is_subscribed: bool = False,
    is_based: bool = False,
    is_pro: bool = False,
    expired: bool = False,
) -> InlineKeyboardMarkup:
    """Create keyboard for premium options based on user's subscription status."""
    try:
        buttons = []

        # Show subscription options for free/expired users
        if not is_subscribed or expired:
            buttons.append([
                InlineKeyboardButton(
                    text=get_message("btn_premium_based", language),
                    callback_data="subscribe_based"
                ),
                InlineKeyboardButton(
                    text=get_message("btn_premium_pro", language),
                    callback_data="subscribe_pro"
                )
            ])

        # Show upgrade option for based tier users
        if is_subscribed and not expired and is_based:
            buttons.append([
                InlineKeyboardButton(
                    text=get_message("btn_premium_upgrade_pro", language),
                    callback_data="upgrade_pro"
                )
            ])

        # Show management options for subscribed users
        if is_subscribed and not expired:
            buttons.append([
                InlineKeyboardButton(
                    text=get_message("btn_premium_cancel_subscription", language),
                    callback_data="cancel_subscription"
                ),
                InlineKeyboardButton(
                    text=get_message("btn_premium_support", language),
                    callback_data="support"
                )
            ])

        # Always add back button
        buttons.append([
            InlineKeyboardButton(
                text=get_message("btn_back", language),
                callback_data="back_to_menu"
            )
        ])

        return InlineKeyboardMarkup(buttons)

    except Exception as e:
        logger.error(f"Error creating premium options keyboard: {str(e)}", exc_info=True)
        # Fallback to simple back button
        return InlineKeyboardMarkup([[
            InlineKeyboardButton(
                text=get_message("btn_back", language),
                callback_data="back_to_menu"
            )
        ]])


def create_premium_upgrade_keyboard(language: str) -> InlineKeyboardMarkup:
    """Create keyboard for premium upgrade view."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_message("btn_premium_upgrade_pro", language),
                callback_data="upgrade_pro"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_message("btn_premium_back", language),
                callback_data="back_to_menu"
            )
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def create_subscription_cancel_keyboard(language: str) -> InlineKeyboardMarkup:
    """Create keyboard for subscription cancellation confirmation."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_message("btn_confirm_cancel", language),
                callback_data="confirm_cancel_subscription"
            ),
            InlineKeyboardButton(
                text=get_message("btn_keep_subscription", language),
                callback_data="keep_subscription"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_message("btn_back", language),
                callback_data="back_to_premium"
            )
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def create_subscription_cancelled_keyboard(language: str) -> InlineKeyboardMarkup:
    """Create keyboard after subscription cancellation."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_message("btn_back", language),
                callback_data="back_to_premium"
            )
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def create_support_menu_keyboard(language: str) -> InlineKeyboardMarkup:
    """Create keyboard for support menu."""
    try:
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_message("btn_support_chat_bot", language),
                    url="https://t.me/sumari_support_bot"
                ),
                InlineKeyboardButton(
                    text=get_message("btn_support_community", language),
                    url="https://t.me/sumari_community"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_message("btn_support_back", language),
                    callback_data="back_to_premium"
                )
            ],
        ]
        return InlineKeyboardMarkup(buttons)
    except Exception as e:
        logger.error(f"Error creating support menu keyboard: {str(e)}", exc_info=True)
        # Create a simple back button keyboard as fallback
        buttons = [
            [
                InlineKeyboardButton(
                    text=get_message("btn_back", language),
                    callback_data="back_to_premium"
                )
            ],
        ]
        return InlineKeyboardMarkup(buttons)
