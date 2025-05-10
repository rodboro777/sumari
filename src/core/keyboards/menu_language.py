
from telegram import InlineKeyboardMarkup
from src.core.localization import get_message
from src.core.keyboards.menu import create_keyboard
from src.core.utils.language_config import MENU_LANGUAGE_OPTIONS


def create_menu_language_selection_keyboard(
    language: str, current_lang: str = None
) -> InlineKeyboardMarkup:
    """Create menu language selection keyboard with only English and Russian options.

    Args:
        language: Interface language code
        current_lang: Currently selected language (to show checkmark)
    """
    buttons = []
    row = []

    # Add language options with checkmarks in a single row
    for lang_code, lang_name in MENU_LANGUAGE_OPTIONS.items():
        display_name = f"✅ {lang_name}" if lang_code == current_lang else lang_name
        button = {
            "text": display_name,
            "callback_data": f"set_menu_lang_{lang_code}",
        }
        row.append(button)

    # Add the row of language buttons
    if row:
        buttons.append(row)

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
