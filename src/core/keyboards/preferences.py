"""Preferences-related keyboard layouts."""

from typing import Dict
from telegram import InlineKeyboardMarkup

from .base import create_keyboard, ButtonData

PREFERENCES_BUTTONS = {
    "language": {
        "text": {"en": "🌐 Interface Language", "ru": "🌐 Язык интерфейса"},
        "callback_data": "show_language_from_prefs",
    },
    "summary_language": {
        "text": {"en": "📝 Summary Language", "ru": "📝 Язык резюме"},
        "callback_data": "show_summary_language",
    },
    "summary_length": {
        "text": {"en": "📏 Summary Length", "ru": "📏 Длина резюме"},
        "callback_data": "show_length_options",
    },
    "audio_settings": {
        "text": {"en": "🎧 Audio Settings", "ru": "🎧 Настройки аудио"},
        "callback_data": "audio_settings",
    },
    "back": {
        "text": {"en": "⬅️ Back", "ru": "⬅️ Назад"},
        "callback_data": "back_to_menu",
    },
}

LANGUAGE_OPTIONS = {
    "en": {
        "text": {"en": "🇬🇧 English", "ru": "🇬🇧 Английский"},
        "callback_data": "lang_en",
    },
    "ru": {
        "text": {"en": "🇷🇺 Russian", "ru": "🇷🇺 Русский"},
        "callback_data": "lang_ru",
    },
    "es": {
        "text": {"en": "🇪🇸 Spanish", "ru": "🇪🇸 Испанский"},
        "callback_data": "lang_es",
    },
    "fr": {
        "text": {"en": "🇫🇷 French", "ru": "🇫🇷 Французский"},
        "callback_data": "lang_fr",
    },
    "de": {
        "text": {"en": "🇩🇪 German", "ru": "🇩🇪 Немецкий"},
        "callback_data": "lang_de",
    },
    "it": {
        "text": {"en": "🇮🇹 Italian", "ru": "🇮🇹 Итальянский"},
        "callback_data": "lang_it",
    },
    "pt": {
        "text": {"en": "🇵🇹 Portuguese", "ru": "🇵🇹 Португальский"},
        "callback_data": "lang_pt",
    },
    "nl": {
        "text": {"en": "🇳🇱 Dutch", "ru": "🇳🇱 Голландский"},
        "callback_data": "lang_nl",
    },
    "pl": {
        "text": {"en": "🇵🇱 Polish", "ru": "🇵🇱 Польский"},
        "callback_data": "lang_pl",
    },
    "uk": {
        "text": {"en": "🇺🇦 Ukrainian", "ru": "🇺🇦 Украинский"},
        "callback_data": "lang_uk",
    },
    "tr": {
        "text": {"en": "🇹🇷 Turkish", "ru": "🇹🇷 Турецкий"},
        "callback_data": "lang_tr",
    },
    "ar": {
        "text": {"en": "🇸🇦 Arabic", "ru": "🇸🇦 Арабский"},
        "callback_data": "lang_ar",
    },
    "hi": {
        "text": {"en": "🇮🇳 Hindi", "ru": "🇮🇳 Хинди"},
        "callback_data": "lang_hi",
    },
    "bn": {
        "text": {"en": "🇧🇩 Bengali", "ru": "🇧🇩 Бенгальский"},
        "callback_data": "lang_bn",
    },
    "ja": {
        "text": {"en": "🇯🇵 Japanese", "ru": "🇯🇵 Японский"},
        "callback_data": "lang_ja",
    },
    "ko": {
        "text": {"en": "🇰🇷 Korean", "ru": "🇰🇷 Корейский"},
        "callback_data": "lang_ko",
    },
    "zh": {
        "text": {"en": "🇨🇳 Chinese", "ru": "🇨🇳 Китайский"},
        "callback_data": "lang_zh",
    },
}

LENGTH_OPTIONS = {
    "short": {
        "text": {"en": "📄 Short", "ru": "📄 Краткое"},
        "callback_data": "set_length_short",
    },
    "medium": {
        "text": {"en": "📑 Medium", "ru": "📑 Среднее"},
        "callback_data": "set_length_medium",
    },
    "detailed": {
        "text": {"en": "📚 Detailed", "ru": "📚 Подробное"},
        "callback_data": "set_length_detailed",
    },
}

AUDIO_OPTIONS = {
    "enabled": {
        "text": {"en": "🔊 Enable Audio", "ru": "🔊 Включить аудио"},
        "callback_data": "set_audio_enabled",
    },
    "disabled": {
        "text": {"en": "🔇 Disable Audio", "ru": "🔇 Отключить аудио"},
        "callback_data": "set_audio_disabled",
    },
}

VOICE_GENDER_OPTIONS = {
    "male": {
        "text": {"en": "👨 Male Voice", "ru": "👨 Мужской голос"},
        "callback_data": "set_voice_male",
    },
    "female": {
        "text": {"en": "👩 Female Voice", "ru": "👩 Женский голос"},
        "callback_data": "set_voice_female",
    },
}


def create_preferences_keyboard(
    language: str, is_pro: bool = False
) -> InlineKeyboardMarkup:
    """Create keyboard for preferences menu."""
    buttons = [
        [PREFERENCES_BUTTONS["language"]],
        [PREFERENCES_BUTTONS["summary_language"]],
        [PREFERENCES_BUTTONS["summary_length"]],
    ]

    # Add pro-only buttons if user is pro
    if is_pro:
        buttons.append([PREFERENCES_BUTTONS["audio_settings"]])

    buttons.append([PREFERENCES_BUTTONS["back"]])
    return create_keyboard(buttons, language)


def create_language_selection_keyboard(
    language: str, setting_type: str = "interface", source: str = "preferences"
) -> InlineKeyboardMarkup:
    """Create keyboard for language selection.

    Args:
        language: Interface language
        setting_type: Type of language setting ('interface' or 'summary')
        source: Where the menu was opened from ('preferences' or 'main_menu')
    """
    # For interface language, only show English and Russian
    if setting_type == "interface":
        buttons = [
            [LANGUAGE_OPTIONS["en"]],
            [LANGUAGE_OPTIONS["ru"]],
        ]
    else:
        # For summary, show all supported languages in a grid
        buttons = []
        row = []
        for i, (lang_code, lang_data) in enumerate(LANGUAGE_OPTIONS.items()):
            row.append(lang_data)
            if len(row) == 2 or i == len(LANGUAGE_OPTIONS) - 1:
                buttons.append(row)
                row = []

    # Add back button with appropriate callback based on source
    back_callback = "back_to_menu" if source == "main_menu" else "back_to_preferences"
    buttons.append([{**PREFERENCES_BUTTONS["back"], "callback_data": back_callback}])

    # Update callback data based on setting type
    if setting_type != "interface":
        for row in buttons[:-1]:  # Skip back button
            for button in row:
                original_lang = button["callback_data"].split("_")[-1]
                button["callback_data"] = f"set_{setting_type}_lang_{original_lang}"

    return create_keyboard(buttons, language)


def create_length_selection_keyboard(language: str) -> InlineKeyboardMarkup:
    """Create keyboard for summary length selection."""
    buttons = [
        [LENGTH_OPTIONS["short"]],
        [LENGTH_OPTIONS["medium"]],
        [LENGTH_OPTIONS["detailed"]],
        [{**PREFERENCES_BUTTONS["back"], "callback_data": "back_to_preferences"}],
    ]
    return create_keyboard(buttons, language)


def create_audio_settings_keyboard(
    language: str, audio_enabled: bool = False, current_gender: str = "female"
) -> InlineKeyboardMarkup:
    """Create keyboard for audio settings.

    Args:
        language: Interface language
        audio_enabled: Whether audio is currently enabled
        current_gender: Current voice gender selection ('male' or 'female')
    """
    buttons = [
        # Audio toggle button
        [AUDIO_OPTIONS["disabled" if audio_enabled else "enabled"]],
        # Voice gender selection - show both options, highlight current
        [
            {
                **VOICE_GENDER_OPTIONS["male"],
                "text": (
                    {"en": "👨 Male Voice ✓", "ru": "👨 Мужской голос ✓"}
                    if current_gender == "male"
                    else VOICE_GENDER_OPTIONS["male"]["text"]
                ),
            },
            {
                **VOICE_GENDER_OPTIONS["female"],
                "text": (
                    {"en": "👩 Female Voice ✓", "ru": "👩 Женский голос ✓"}
                    if current_gender == "female"
                    else VOICE_GENDER_OPTIONS["female"]["text"]
                ),
            },
        ],
        # Language selection button
        [
            {
                "text": {"en": "🌐 Voice Language", "ru": "🌐 Язык голоса"},
                "callback_data": "show_voice_language",
            }
        ],
        # Demo button
        [
            {
                "text": {"en": "🎧 Try Voice", "ru": "🎧 Прослушать"},
                "callback_data": "voice_demo",
            }
        ],
        # Back button
        [{**PREFERENCES_BUTTONS["back"], "callback_data": "back_to_preferences"}],
    ]
    return create_keyboard(buttons, language)
