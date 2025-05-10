from telegram import InlineKeyboardMarkup
from src.core.localization import get_message
from src.core.keyboards.menu import create_keyboard


def create_summary_keyboard(language: str, is_pro: bool = False) -> InlineKeyboardMarkup:
    """Create keyboard for summary response."""
    buttons = [
        [
            {
                "text": get_message("btn_summary_regenerate", language),
                "callback_data": "regenerate_summary",
            }
        ],
        [
            {
                "text": get_message("btn_summary_voice", language),
                "callback_data": "voice_summary",
            }
        ] if is_pro else [],
        [
            {
                "text": get_message("btn_summary_language", language),
                "callback_data": "change_summary_language",
            }
        ],
        [
            {
                "text": get_message("btn_back", language),
                "callback_data": "back_to_menu",
            }
        ],
    ]
    
    # Remove empty rows (when not pro)
    buttons = [row for row in buttons if row]
    
    return create_keyboard(buttons, language)