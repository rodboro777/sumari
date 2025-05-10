"""Voice-related keyboard layouts."""

from telegram import InlineKeyboardMarkup

from .menu import create_keyboard
from src.core.utils.language_config import LANGUAGE_OPTIONS
from src.core.localization import get_message


def create_voice_selection_keyboard(
    language: str, audio_enabled: bool = False, current_gender: str = "female"
) -> InlineKeyboardMarkup:
    """Create keyboard for voice selection (male/female).

    Args:
        language: Interface language
        audio_enabled: Whether audio summaries are enabled
        current_gender: Current voice gender setting

    Returns:
        Voice selection keyboard
    """
    buttons = []

    # Add audio toggle button
    buttons.append([
        {
            "text": get_message("btn_audio_toggle", language) if audio_enabled else get_message("btn_audio_enable", language),
            "callback_data": "set_audio_disabled" if audio_enabled else "set_audio_enabled",
        }
    ])

    # Add gender selection buttons
    buttons.append([
        {
            "text": ("✅ " if gender == current_gender else "") + get_message(f"btn_voice_{gender}", language),
            "callback_data": f"set_voice_{gender}",
        }
        for gender in ["male", "female"]
    ])

    # Add language selection button
    buttons.append([
        {
            "text": get_message("btn_voice_language", language),
            "callback_data": "voice_language_menu",
        }
    ])

    # Add back button
    buttons.append([
        {
            "text": get_message("btn_voice_back", language),
            "callback_data": "back_to_preferences",
        }
    ])
    return create_keyboard(buttons, language)


def create_voice_language_keyboard(language: str = "en") -> InlineKeyboardMarkup:
    """Create keyboard for voice language selection."""
    buttons = []
    row = []

    # Add all languages in a grid layout (2 per row)
    for i, (lang_code, lang_name) in enumerate(LANGUAGE_OPTIONS.items()):
        # Create a new button with voice-specific callback
        button = {
            "text": lang_name,
            "callback_data": f"set_voice_lang_{lang_code}",
        }
        row.append(button)
        if len(row) == 2 or i == len(LANGUAGE_OPTIONS) - 1:
            buttons.append(row)
            row = []

    # Add back button with correct callback
    buttons.append(
        [
            {
                "text": get_message("btn_voice_back", language),
                "callback_data": "audio_settings",  # This will return to audio settings
            }
        ]
    )

    return create_keyboard(buttons, language)
