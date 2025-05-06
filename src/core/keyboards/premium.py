"""Premium-related keyboard layouts."""

from typing import Dict, Optional
import logging
from telegram import InlineKeyboardMarkup

from .base import create_keyboard
from .payment import create_payment_method_keyboard
from src.core.localization import get_message

logger = logging.getLogger(__name__)

PREMIUM_BUTTONS = {
    "extend_based": {
        "callback_data": "extend_based",
    },
    "extend_pro": {
        "callback_data": "extend_pro",
    },
    "upgrade_pro": {
        "callback_data": "upgrade_pro",
    },
    "cancel_subscription": {
        "callback_data": "cancel_subscription_confirm",
    },
    "support": {
        "callback_data": "show_support_menu",
    },
    "back": {
        "callback_data": "back_to_menu",
    },
}

PAYMENT_BUTTONS = {
    "stripe": {
        "callback_data": "payment_stripe",
    },
    "nowpayments": {
        "callback_data": "payment_nowpayments",
    },
    "back": {
        "callback_data": "back_to_premium",
    },
}

SUPPORT_BUTTONS = {
    "chat_bot": {
        "url": "https://t.me/sumari_support_bot",
    },
    "community": {
        "url": "https://t.me/sumari_community",
    },
    "back": {
        "callback_data": "back_to_premium",
    },
}


def create_premium_options_keyboard(
    language: str,
    is_subscribed: bool = False,
    is_based: bool = False,
    is_pro: bool = False,
    expired: bool = False,
) -> InlineKeyboardMarkup:
    """Create keyboard for premium options."""
    try:
        buttons = []

        # Show appropriate subscription options
        if not is_subscribed or expired:
            buttons.append(
                [
                    {
                        "text": get_message("btn_premium_based", language),
                        "callback_data": "subscribe_based",
                    },
                    {
                        "text": get_message("btn_premium_pro", language),
                        "callback_data": "subscribe_pro",
                    },
                ]
            )

        # Show subscription management options
        if is_subscribed and not expired:
            if is_pro:
                buttons.append(
                    [
                        {
                            "text": get_message("btn_premium_extend_pro", language),
                            "callback_data": PREMIUM_BUTTONS["extend_pro"][
                                "callback_data"
                            ],
                        }
                    ]
                )
            else:
                buttons.extend(
                    [
                        [
                            {
                                "text": get_message(
                                    "btn_premium_extend_based", language
                                ),
                                "callback_data": PREMIUM_BUTTONS["extend_based"][
                                    "callback_data"
                                ],
                            }
                        ],
                        [
                            {
                                "text": get_message(
                                    "btn_premium_upgrade_pro", language
                                ),
                                "callback_data": PREMIUM_BUTTONS["upgrade_pro"][
                                    "callback_data"
                                ],
                            }
                        ],
                    ]
                )

            # Add subscription management and support buttons
            buttons.append(
                [
                    {
                        "text": get_message(
                            "btn_premium_cancel_subscription", language
                        ),
                        "callback_data": PREMIUM_BUTTONS["cancel_subscription"][
                            "callback_data"
                        ],
                    },
                    {
                        "text": get_message("btn_premium_support", language),
                        "callback_data": PREMIUM_BUTTONS["support"]["callback_data"],
                    },
                ]
            )

        # Add back button
        buttons.append(
            [
                {
                    "text": get_message("btn_back", language),
                    "callback_data": PREMIUM_BUTTONS["back"]["callback_data"],
                }
            ]
        )

        return create_keyboard(buttons, language)
    except Exception as e:
        logger.error(
            f"Error creating premium options keyboard: {str(e)}", exc_info=True
        )
        # Create a simple back button keyboard as fallback
        buttons = [
            [
                {
                    "text": get_message("btn_back", language),
                    "callback_data": "back_to_menu",
                }
            ]
        ]
        return create_keyboard(buttons, language)


def create_premium_status_keyboard(language: str) -> InlineKeyboardMarkup:
    """Create keyboard for premium status view."""
    buttons = [
        [
            {
                "text": get_message("btn_premium_extend_pro", language),
                "callback_data": PREMIUM_BUTTONS["extend_pro"]["callback_data"],
            }
        ],
        [
            {
                "text": get_message("btn_premium_upgrade_pro", language),
                "callback_data": PREMIUM_BUTTONS["upgrade_pro"]["callback_data"],
            }
        ],
        [
            {
                "text": get_message("btn_premium_back", language),
                "callback_data": PREMIUM_BUTTONS["back"]["callback_data"],
            }
        ],
    ]
    return create_keyboard(buttons, language)


def create_support_menu_keyboard(language: str) -> InlineKeyboardMarkup:
    """Create keyboard for support menu."""
    try:
        buttons = [
            [
                {
                    "text": get_message("btn_support_chat_bot", language),
                    "url": SUPPORT_BUTTONS["chat_bot"]["url"],
                },
                {
                    "text": get_message("btn_support_community", language),
                    "url": SUPPORT_BUTTONS["community"]["url"],
                },
            ],
            [
                {
                    "text": get_message("btn_support_back", language),
                    "callback_data": SUPPORT_BUTTONS["back"]["callback_data"],
                }
            ],
        ]
        return create_keyboard(buttons, language)
    except Exception as e:
        logger.error(f"Error creating support menu keyboard: {str(e)}", exc_info=True)
        # Create a simple back button keyboard as fallback
        buttons = [
            [
                {
                    "text": get_message("btn_back", language),
                    "callback_data": "back_to_premium",
                }
            ],
        ]
        return create_keyboard(buttons, language)
