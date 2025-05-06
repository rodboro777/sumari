"""Preferences-related keyboard layouts."""

from typing import Dict, List
from telegram import InlineKeyboardMarkup

from .base import create_keyboard, ButtonData
from src.core.localization import get_message

PREFERENCES_BUTTONS = {
    "summary_length": {
        "callback_data": "show_summary_length",
    },
    "summary_language": {
        "callback_data": "show_summary_language",
    },
    "voice_settings": {
        "callback_data": "show_voice_settings",
    },
    "back": {
        "callback_data": "back_to_menu",
    },
}

LANGUAGE_OPTIONS = {
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский",
    "es": "🇪🇸 Español",
    "fr": "🇫🇷 Français",
    "de": "🇩🇪 Deutsch",
    "it": "🇮🇹 Italiano",
    "pt": "🇵🇹 Português",
    "nl": "🇳🇱 Nederlands",
    "pl": "🇵🇱 Polski",
    "uk": "🇺🇦 Українська",
    "tr": "🇹🇷 Türkçe",
    "ar": "🇸🇦 العربية",
    "hi": "🇮🇳 हिन्दी",
    "bn": "🇧🇩 বাংলা",
    "id": "🇮🇩 Indonesia",
    "ja": "🇯🇵 日本語",
    "ko": "🇰🇷 한국어",
    "th": "🇹🇭 ไทย",
    "vi": "🇻🇳 Tiếng Việt",
    "zh": "🇨🇳 中文",
}

MENU_LANGUAGE_OPTIONS = {
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский",
}


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
                "callback_data": PREFERENCES_BUTTONS["summary_length"]["callback_data"],
            }
        ],
        [
            {
                "text": get_message("btn_pref_summary_language", language),
                "callback_data": PREFERENCES_BUTTONS["summary_language"][
                    "callback_data"
                ],
            }
        ],
    ]

    # Only show voice settings for pro users
    if is_pro:
        buttons.append(
            [
                {
                    "text": get_message("btn_pref_voice_settings", language),
                    "callback_data": PREFERENCES_BUTTONS["voice_settings"][
                        "callback_data"
                    ],
                }
            ]
        )

    buttons.append(
        [
            {
                "text": get_message("btn_pref_back", language),
                "callback_data": PREFERENCES_BUTTONS["back"]["callback_data"],
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


def create_menu_language_selection_keyboard(
    language: str, current_lang: str = None
) -> InlineKeyboardMarkup:
    """Create menu language selection keyboard with only English and Russian options.

    Args:
        language: Interface language code
        current_lang: Currently selected language (to show checkmark)
    """
    buttons = []

    # Add language options with checkmarks
    for lang_code, lang_name in MENU_LANGUAGE_OPTIONS.items():
        display_name = f"✅ {lang_name}" if lang_code == current_lang else lang_name
        button = {
            "text": display_name,
            "callback_data": f"lang_{lang_code}",
        }
        buttons.append([button])

    # Add back button
    buttons.append(
        [
            {
                "text": get_message("btn_back", language),
                "callback_data": "back_to_menu",
            }
        ]
    )

    return create_keyboard(buttons, language)
