"""Base keyboard functionality and common utilities."""

from typing import List, Dict, Union
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.core.localization import get_message

# Type aliases
KeyboardType = List[List[InlineKeyboardButton]]
ButtonData = Dict[str, Union[str, Dict[str, str]]]

MAIN_MENU_BUTTONS = {
    "language": {
        "callback_data": "lang_menu",
    },
    "preferences": {
        "callback_data": "preferences",
    },
    "help": {
        "callback_data": "help",
    },
    "premium": {
        "callback_data": "premium",
    },
    "account": {
        "callback_data": "my_account",
    },
}


def create_main_menu_keyboard(language: str) -> InlineKeyboardMarkup:
    """Create main menu keyboard with language-specific labels."""
    buttons = [
        [
            {
                "text": get_message("btn_language", language),
                "callback_data": MAIN_MENU_BUTTONS["language"]["callback_data"],
            },
            {
                "text": get_message("btn_preferences", language),
                "callback_data": MAIN_MENU_BUTTONS["preferences"]["callback_data"],
            },
        ],
        [
            {
                "text": get_message("btn_help", language),
                "callback_data": MAIN_MENU_BUTTONS["help"]["callback_data"],
            },
            {
                "text": get_message("btn_premium", language),
                "callback_data": MAIN_MENU_BUTTONS["premium"]["callback_data"],
            },
        ],
        [
            {
                "text": get_message("btn_account", language),
                "callback_data": MAIN_MENU_BUTTONS["account"]["callback_data"],
            }
        ],
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
            # Create button kwargs based on what's available
            button_kwargs = {"text": button["text"]}

            # Add URL if present
            if "url" in button:
                button_kwargs["url"] = button["url"]
            # Add callback_data if present and no URL
            elif "callback_data" in button:
                button_kwargs["callback_data"] = button["callback_data"]

            keyboard_row.append(InlineKeyboardButton(**button_kwargs))
        keyboard.append(keyboard_row)
    return InlineKeyboardMarkup(keyboard)


def create_back_button(
    language: str, callback_data: str = "back_to_menu"
) -> InlineKeyboardMarkup:
    """Create a simple back button."""
    buttons = [
        [
            {
                "text": get_message("btn_back", language),
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
                text=get_message(button["text"], language),
                callback_data=button["callback_data"],
            )
        )

        if len(row) == columns:
            keyboard.append(row)
            row = []

    if row:  # Add any remaining buttons
        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)
