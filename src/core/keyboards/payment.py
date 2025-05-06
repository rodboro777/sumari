"""Payment-related keyboard layouts."""

from typing import Dict, Optional
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from .base import create_keyboard
from src.core.localization import get_message


PAYMENT_BUTTONS = {
    "stripe": {
        "callback_data": "provider_stripe",
    },
    "nowpayments": {
        "callback_data": "provider_nowpayments",
    },
    "back": {
        "callback_data": "back_to_premium",
    },
}

def create_payment_method_keyboard(language: str, tier: str) -> InlineKeyboardMarkup:
    """Create keyboard for payment method selection."""
    buttons = [
        [
            {
                "text": get_message("btn_payment_stripe", language),
                "callback_data": f"provider_stripe_{tier}",
            }
        ],
        [
            {
                "text": get_message("btn_payment_crypto", language),
                "callback_data": f"provider_nowpayments_{tier}",
            }
        ],
        [
            {
                "text": get_message("btn_payment_back", language),
                "callback_data": PAYMENT_BUTTONS["back"]["callback_data"],
            }
        ],
    ]
    return create_keyboard(buttons, language)



def create_currency_keyboard(
    language: str, payment_type: str, tier: str
) -> InlineKeyboardMarkup:
    """Create keyboard for currency selection."""
    buttons = []

    # Add currency groups
    for currency_group in ["major", "international", "asian"]:
        row = []
        for currency in CURRENCY_BUTTONS[currency_group]:
            button_data = {
                "text": {language: currency["text"]},
                "callback_data": f"{payment_type}_{tier}_{currency['callback_data'].split('_')[1]}",
            }
            row.append(button_data)
        buttons.append(row)

    # Add back button
    buttons.append(
        [
            {
                "text": get_message("btn_payment_back", language),
                "callback_data": PAYMENT_BUTTONS["back"]["callback_data"],
            }
        ]
    )

    return create_keyboard(buttons, language)


def create_payment_link_keyboard(
    payment_url: str, language: str = "en"
) -> InlineKeyboardMarkup:
    """Create a keyboard with a payment link button."""
    keyboard = [
        [
            InlineKeyboardButton(
                text=get_message("btn_payment_stripe", language), url=payment_url
            )
        ],
        [
            InlineKeyboardButton(
                text=get_message("btn_payment_back", language),
                callback_data=PAYMENT_BUTTONS["back"]["callback_data"],
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
