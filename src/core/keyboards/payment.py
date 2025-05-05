"""Payment-related keyboard layouts."""

from typing import Dict
from telegram import InlineKeyboardMarkup

from .base import create_keyboard, ButtonData

PAYMENT_BUTTONS = {
    "card": {
        "text": {"en": "💳 Pay with Card", "ru": "💳 Оплатить картой"},
        "callback_data": "payment_card",
    },
    "crypto": {
        "text": {"en": "💎 Pay with Crypto", "ru": "💎 Оплатить криптовалютой"},
        "callback_data": "payment_crypto",
    },
    "stripe": {
        "text": {"en": "Stripe", "ru": "Stripe"},
        "callback_data": "provider_stripe",
    },
    "nowpayments": {
        "text": {"en": "NOWPayments", "ru": "NOWPayments"},
        "callback_data": "provider_nowpayments",
    },
    "ton": {"text": {"en": "TON", "ru": "TON"}, "callback_data": "provider_ton"},
    "check_payment": {
        "text": {"en": "✅ Check Payment", "ru": "✅ Проверить платеж"},
        "callback_data": "check_payment",
    },
    "back": {
        "text": {"en": "⬅️ Back", "ru": "⬅️ Назад"},
        "callback_data": "back_to_premium",
    },
}


def create_payment_method_keyboard(language: str, tier: str) -> InlineKeyboardMarkup:
    """Create keyboard for payment method selection."""
    buttons = [
        [{**PAYMENT_BUTTONS["card"], "callback_data": f"payment_card_{tier}"}],
        [{**PAYMENT_BUTTONS["crypto"], "callback_data": f"payment_crypto_{tier}"}],
        [PAYMENT_BUTTONS["back"]],
    ]
    return create_keyboard(buttons, language)


def create_payment_provider_keyboard(
    language: str, payment_type: str, tier: str
) -> InlineKeyboardMarkup:
    """Create keyboard for payment provider selection."""
    buttons = []

    if payment_type == "card":
        buttons.append(
            [{**PAYMENT_BUTTONS["stripe"], "callback_data": f"provider_stripe_{tier}"}]
        )
    else:  # crypto
        buttons.extend([
            [{**PAYMENT_BUTTONS["nowpayments"], "callback_data": f"provider_nowpayments_{tier}"}],
            [{**PAYMENT_BUTTONS["ton"], "callback_data": f"provider_ton_{tier}"}]
        ])

    buttons.append(
        [{**PAYMENT_BUTTONS["back"], "callback_data": f"payment_method_{tier}"}]
    )

    return create_keyboard(buttons, language)


def create_ton_payment_keyboard(language: str, tier: str) -> InlineKeyboardMarkup:
    """Create keyboard for TON payment process."""
    buttons = [
        [{**PAYMENT_BUTTONS["check_payment"], "callback_data": f"check_ton_{tier}"}],
        [PAYMENT_BUTTONS["back"]],
    ]
    return create_keyboard(buttons, language)


# Currency selection keyboard data
CURRENCY_BUTTONS = {
    "major": [
        {"text": "EUR €", "callback_data": "currency_eur"},
        {"text": "USD $", "callback_data": "currency_usd"},
        {"text": "GBP £", "callback_data": "currency_gbp"},
    ],
    "international": [
        {"text": "AUD A$", "callback_data": "currency_aud"},
        {"text": "CAD C$", "callback_data": "currency_cad"},
        {"text": "CHF Fr", "callback_data": "currency_chf"},
    ],
    "asian": [
        {"text": "JPY ¥", "callback_data": "currency_jpy"},
        {"text": "SGD S$", "callback_data": "currency_sgd"},
        {"text": "HKD HK$", "callback_data": "currency_hkd"},
    ],
}


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
    buttons.append([PAYMENT_BUTTONS["back"]])

    return create_keyboard(buttons, language)
