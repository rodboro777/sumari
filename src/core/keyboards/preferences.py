"""Preferences-related keyboard layouts."""

from telegram import InlineKeyboardMarkup

from .menu import create_keyboard
from src.core.localization import get_message
from src.core.utils import (
    LANGUAGE_OPTIONS,
    
)   


def create_preferences_keyboard(
    language: str, is_pro: bool = False
) -> InlineKeyboardMarkup:
    """Create preferences menu keyboard.

    Args:
        language: Interface language code
        is_pro: Whether user has pro status for showing voice settings
    """
    buttons = [
        [
            {
                "text": get_message("btn_pref_summary_length", language),
                "callback_data": "show_summary_length",
            }
        ],
        [
            {
                "text": get_message("btn_pref_summary_language", language),
                "callback_data": "show_summary_language",
            }
        ],
    ]

    # Only show voice settings for pro users
    if is_pro:
        buttons.append(
            [
                {
                    "text": get_message("btn_pref_voice_settings", language),
                    "callback_data": "show_voice_settings",
                }
            ]
        )

    buttons.append(
        [
            {
                "text": get_message("btn_pref_back", language),
                "callback_data": "back_to_menu",
            }
        ]
    )

    return create_keyboard(buttons, language)


def create_language_selection_keyboard(
    language: str, source: str = "main_menu", current_lang: str = None
) -> InlineKeyboardMarkup:
    """Create language selection keyboard.

    Args:
        language: Interface language code
        source: Source menu to return to
        current_lang: Currently selected language (to show checkmark)
    """
    buttons = []
    row = []

    # Add all languages in a grid layout (2 per row)
    for i, (lang_code, lang_name) in enumerate(LANGUAGE_OPTIONS.items()):
        # Add checkmark if this is the selected language
        display_name = f"✔️ {lang_name}" if lang_code == current_lang else lang_name

        # Create button with appropriate callback
        button = {
            "text": display_name,
            "callback_data": (
                f"set_summary_lang_{lang_code}"
                if source == "preferences"
                else f"lang_{lang_code}"
            ),
        }
        row.append(button)
        if len(row) == 2 or i == len(LANGUAGE_OPTIONS) - 1:
            buttons.append(row)
            row = []

    # Add back button with correct callback
    back_callback = "back_to_preferences" if source == "preferences" else "back_to_menu"
    buttons.append(
        [
            {
                "text": get_message("btn_back", language),
                "callback_data": back_callback,
            }
        ]
    )

    return create_keyboard(buttons, language)


def create_summary_length_keyboard(
    language: str, current_length: str = None
) -> InlineKeyboardMarkup:
    """Create summary length selection keyboard.

    Args:
        language: Interface language code
        current_length: Currently selected length (to show checkmark)
    """
    # Define length options with their callbacks
    length_options = [
        {
            "text": get_message("btn_summary_short", language),
            "callback_data": "set_length_short",
            "value": "short",
        },
        {
            "text": get_message("btn_summary_medium", language),
            "callback_data": "set_length_medium",
            "value": "medium",
        },
        {
            "text": get_message("btn_summary_detailed", language),
            "callback_data": "set_length_detailed",
            "value": "detailed",
        },
    ]

    buttons = []
    row = []

    # Add length options with checkmarks
    for option in length_options:
        display_text = (
            f"✅ {option['text']}"
            if option["value"] == current_length
            else option["text"]
        )
        button = {"text": display_text, "callback_data": option["callback_data"]}
        row.append(button)
        if len(row) == 2:
            buttons.append(row)
            row = []

    # Add any remaining buttons
    if row:
        buttons.append(row)

    # Add back button
    buttons.append(
        [
            {
                "text": get_message("btn_back", language),
                "callback_data": "back_to_preferences",
            }
        ]
    )

    return create_keyboard(buttons, language)

