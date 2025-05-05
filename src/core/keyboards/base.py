"""Base keyboard functionality and common utilities."""

from typing import List, Dict, Union, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Type aliases
KeyboardType = List[List[InlineKeyboardButton]]
ButtonData = Dict[str, Union[str, Dict[str, str]]]

MAIN_MENU_BUTTONS = {
    "language": {
        "text": {"en": "🌐 Language", "ru": "🌐 Язык"},
        "callback_data": "lang_menu",
    },
    "preferences": {
        "text": {"en": "⚙️ Preferences", "ru": "⚙️ Настройки"},
        "callback_data": "preferences",
    },
    "help": {
        "text": {"en": "❓ Help & About", "ru": "❓ Помощь и О боте"},
        "callback_data": "help",
    },
    "premium": {
        "text": {"en": "⭐ Premium", "ru": "⭐ Премиум"},
        "callback_data": "premium",
    },
    "account": {
        "text": {"en": "👤 My Account", "ru": "👤 Мой аккаунт"},
        "callback_data": "my_account",
    },
}


def create_main_menu_keyboard(language: str) -> InlineKeyboardMarkup:
    """Create main menu keyboard with language-specific labels."""
    buttons = [
        [MAIN_MENU_BUTTONS["language"], MAIN_MENU_BUTTONS["preferences"]],
        [MAIN_MENU_BUTTONS["help"], MAIN_MENU_BUTTONS["premium"]],
        [MAIN_MENU_BUTTONS["account"]],
    ]
    return create_keyboard(buttons, language)


def create_keyboard(
    buttons: List[List[ButtonData]], language: str
) -> InlineKeyboardMarkup:
    """
    Create a keyboard from a list of button data.

    Args:
        buttons: List of lists of button data (for rows and columns)
        language: Language code for button text

    Returns:
        InlineKeyboardMarkup: The constructed keyboard
    """
    keyboard = []
    for row in buttons:
        keyboard_row = []
        for button in row:
            text = button.get("text", {}).get(
                language, button.get("text", {}).get("en", "")
            )
            callback_data = button.get("callback_data", "")
            url = button.get("url", None)

            if url:
                keyboard_row.append(InlineKeyboardButton(text=text, url=url))
            else:
                keyboard_row.append(
                    InlineKeyboardButton(text=text, callback_data=callback_data)
                )
        keyboard.append(keyboard_row)

    return InlineKeyboardMarkup(keyboard)


def create_back_button(
    language: str, callback_data: str = "back_to_menu"
) -> InlineKeyboardMarkup:
    """Create a simple back button."""
    buttons = [
        [
            {
                "text": {"en": "⬅️ Back to Menu", "ru": "⬅️ Вернуться в меню"},
                "callback_data": callback_data,
            }
        ]
    ]
    return create_keyboard(buttons, language)


def create_simple_keyboard(
    buttons: List[Dict[str, str]], language: str, columns: int = 1
) -> InlineKeyboardMarkup:
    """
    Create a simple keyboard with a specified number of columns.

    Args:
        buttons: List of button data
        language: Language code
        columns: Number of buttons per row
    """
    keyboard = []
    row = []

    for button in buttons:
        row.append(
            InlineKeyboardButton(
                text=button["text"], callback_data=button["callback_data"]
            )
        )

        if len(row) == columns:
            keyboard.append(row)
            row = []

    if row:  # Add any remaining buttons
        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)
