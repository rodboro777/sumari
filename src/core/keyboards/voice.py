"""Voice-related keyboard layouts."""

from typing import Dict
from telegram import InlineKeyboardMarkup

from .base import create_keyboard, ButtonData
from .preferences import LANGUAGE_OPTIONS

VOICE_BUTTONS = {
    "male": {
        "text": {"en": "👨 Male Voice", "ru": "👨 Мужской голос"},
        "callback_data": "set_voice_male",
    },
    "female": {
        "text": {"en": "👩 Female Voice", "ru": "👩 Женский голос"},
        "callback_data": "set_voice_female",
    },
    "language": {
        "text": {"en": "🌐 Voice Language", "ru": "🌐 Язык голоса"},
        "callback_data": "show_voice_language",
    },
    "back": {
        "text": {"en": "⬅️ Back", "ru": "⬅️ Назад"},
        "callback_data": "back_to_preferences",
    },
}


def create_voice_selection_keyboard(
    language: str, audio_enabled: bool = False, current_gender: str = "female"
) -> InlineKeyboardMarkup:
    """Create keyboard for voice selection (male/female).

    Args:
        language: Interface language
        audio_enabled: Whether audio is enabled
        current_gender: Current voice gender selection
    """
    # Add checkmark to current gender
    male_button = {
        **VOICE_BUTTONS["male"],
        "text": {
            "en": "👨 Male Voice ✓" if current_gender == "male" else "👨 Male Voice",
            "ru": (
                "👨 Мужской голос ✓" if current_gender == "male" else "👨 Мужской голос"
            ),
        },
    }
    female_button = {
        **VOICE_BUTTONS["female"],
        "text": {
            "en": (
                "👩 Female Voice ✓" if current_gender == "female" else "👩 Female Voice"
            ),
            "ru": (
                "👩 Женский голос ✓"
                if current_gender == "female"
                else "👩 Женский голос"
            ),
        },
    }

    buttons = [
        # Audio toggle and gender selection
        [
            {
                "text": {
                    "en": "🔇 Disable Audio" if audio_enabled else "🔊 Enable Audio",
                    "ru": (
                        "🔇 Отключить аудио" if audio_enabled else "🔊 Включить аудио"
                    ),
                },
                "callback_data": (
                    "set_audio_disabled" if audio_enabled else "set_audio_enabled"
                ),
            }
        ],
        [male_button, female_button],  # Gender buttons on same line
        [VOICE_BUTTONS["language"]],  # Language selection
        [VOICE_BUTTONS["back"]],  # Back button
    ]
    return create_keyboard(buttons, language)


def create_voice_language_keyboard(language: str = "en") -> InlineKeyboardMarkup:
    """Create keyboard for voice language selection."""
    buttons = []
    row = []

    # Add all languages in a grid layout (2 per row)
    for i, (lang_code, lang_data) in enumerate(LANGUAGE_OPTIONS.items()):
        # Create a new button with voice-specific callback
        button = {
            "text": lang_data["text"],
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
                "text": VOICE_BUTTONS["back"]["text"],
                "callback_data": "audio_settings",  # This will return to audio settings
            }
        ]
    )

    return create_keyboard(buttons, language)
