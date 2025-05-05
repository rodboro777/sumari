"""Premium-related keyboard layouts."""

from typing import Dict
from telegram import InlineKeyboardMarkup

from .base import create_keyboard, ButtonData

PREMIUM_BUTTONS = {
    "based": {
        "text": {"en": "💫 Based ($5/month)", "ru": "💫 База ($5/месяц)"},
        "callback_data": "subscribe_based",
    },
    "pro": {
        "text": {"en": "⭐️ Pro ($20/month)", "ru": "⭐️ Про ($20/месяц)"},
        "callback_data": "subscribe_pro",
    },
    "extend_based": {
        "text": {"en": "🔄 Renew Based", "ru": "🔄 Продлить Based"},
        "callback_data": "payment_method_based",
    },
    "extend_pro": {
        "text": {"en": "🔄 Renew Pro", "ru": "🔄 Продлить Pro"},
        "callback_data": "payment_method_pro",
    },
    "upgrade_pro": {
        "text": {"en": "⭐ Upgrade to Pro", "ru": "⭐ Перейти на Pro"},
        "callback_data": "payment_method_pro",
    },
    "cancel_subscription": {
        "text": {"en": "❌ Cancel", "ru": "❌ Отменить"},
        "callback_data": "cancel_subscription_confirm",
    },
    "support": {
        "text": {"en": "💬 Support", "ru": "💬 Поддержка"},
        "callback_data": "show_support_menu",
    },
    "back": {
        "text": {"en": "⬅️ Back", "ru": "⬅️ Назад"},
        "callback_data": "back_to_menu",
    },
}

SUPPORT_BUTTONS = {
    "chat_bot": {
        "text": {"en": "🤖 Chat with Bot", "ru": "🤖 Чат с ботом"},
        "url": "https://t.me/sumari_support_bot",
    },
    "community": {
        "text": {"en": "👥 Community", "ru": "👥 Сообщество"},
        "url": "https://t.me/sumari_community",
    },
    "back": {
        "text": {"en": "⬅️ Back", "ru": "⬅️ Назад"},
        "callback_data": "back_to_premium",
    },
}


def create_premium_options_keyboard(
    language: str,
    is_subscribed: bool = False,
    is_pro: bool = False,
    expired: bool = False,
) -> InlineKeyboardMarkup:
    """Create keyboard for premium options."""
    buttons = []

    # Show appropriate subscription options
    if not is_subscribed or expired:
        buttons.extend([[PREMIUM_BUTTONS["based"]], [PREMIUM_BUTTONS["pro"]]])
    elif is_subscribed and not expired:
        if is_pro:
            buttons.append([PREMIUM_BUTTONS["extend_pro"]])
        else:
            buttons.extend(
                [[PREMIUM_BUTTONS["extend_based"]], [PREMIUM_BUTTONS["upgrade_pro"]]]
            )

    # Add subscription management and support buttons side by side
    if is_subscribed:
        buttons.append(
            [PREMIUM_BUTTONS["cancel_subscription"], PREMIUM_BUTTONS["support"]]
        )
    else:
        buttons.append([PREMIUM_BUTTONS["support"]])

    # Add back button
    buttons.append([PREMIUM_BUTTONS["back"]])

    return create_keyboard(buttons, language)


def create_premium_status_keyboard(language: str) -> InlineKeyboardMarkup:
    """Create keyboard for premium status view."""
    buttons = [
        [PREMIUM_BUTTONS["extend_pro"]],
        [PREMIUM_BUTTONS["upgrade_pro"]],
        [PREMIUM_BUTTONS["back"]],
    ]
    return create_keyboard(buttons, language)


def create_support_menu_keyboard(language: str) -> InlineKeyboardMarkup:
    """Create keyboard for support menu."""
    buttons = [
        [SUPPORT_BUTTONS["chat_bot"], SUPPORT_BUTTONS["community"]],
        [SUPPORT_BUTTONS["back"]],
    ]
    return create_keyboard(buttons, language)
