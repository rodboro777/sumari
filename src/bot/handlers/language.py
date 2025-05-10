"""Language handlers for the bot."""

# Standard library imports
import logging

# Third-party imports
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from src.core.utils.language_config import LANGUAGE_OPTIONS, MENU_LANGUAGE_OPTIONS
# Local application imports
from src.core.keyboards import (
    create_preferences_keyboard,
    create_language_selection_keyboard,
    create_menu_language_selection_keyboard
)
from src.core.localization import get_message
from src.core.utils import (
    get_user_language,
    get_user_preferences,
    update_user_preferences,
)
from src.core.utils.text import escape_md

# Set up module logger
logger = logging.getLogger(__name__)

async def handle_preferences_language(update: Update, language: str, user_id: int) -> None:
    """Handle language selection from preferences menu."""
    query = update.callback_query
    data = query.data

    preferences = get_user_preferences(user_id)
    current_lang = preferences.get("summary_language", "en")
    
    if data == "show_language_from_prefs":
        # Show summary language selection menu
        new_text = get_message("select_summary_language", language)
        new_markup = create_language_selection_keyboard(language, "preferences", current_lang)
        
        await query.edit_message_text(
            text=new_text, 
            parse_mode=ParseMode.MARKDOWN_V2, 
            reply_markup=new_markup
        )
        return
        
    elif data.startswith("set_summary_lang_"):
        new_lang = data.split("_")[-1]
        try:
            # Don't update if the language hasn't changed
            if new_lang == current_lang:
                await query.answer(
                    get_message("already_selected", language),
                    show_alert=True
                )
                return
                
            # Update summary language in preferences
            preferences["summary_language"] = new_lang
            update_user_preferences(user_id, preferences)

            # Show confirmation and update menu
            await query.answer(
                f"{LANGUAGE_OPTIONS[current_lang]} → {LANGUAGE_OPTIONS[new_lang]}",
                show_alert=True
            )

            new_text = get_message("summary_language_set", language).format(
                language=LANGUAGE_OPTIONS[new_lang]
            )
            new_markup = create_preferences_keyboard(language)

            await query.edit_message_text(
                text=new_text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=new_markup,
            )
        except Exception as e:
            logger.error(f"Error updating preferences language: {e}")
            new_text = get_message("error", language).format(
                error=escape_md("Failed to update language")
            )
            await query.edit_message_text(
                text=new_text, parse_mode=ParseMode.MARKDOWN_V2
            )

async def handle_menu_language(update: Update, language: str, user_id: int) -> None:
    """Handle menu language selection and updates."""
    query = update.callback_query
    data = query.data

    preferences = get_user_preferences(user_id)
    current_lang = preferences.get("menu_language", "en")
    
    if data.startswith("set_menu_lang_"):
        # Extract the language code from the callback data
        new_lang = data.split("_")[-1]
        
        # Validate that the language code is valid
        if new_lang not in MENU_LANGUAGE_OPTIONS:
            logger.error(f"Invalid language code received: {new_lang}")
            return

        try:
            # Don't update if the language hasn't changed
            if new_lang == current_lang:
                await query.answer(
                    get_message("already_selected", language),
                    show_alert=True
                )
                return
                
            # Update menu language in preferences
            preferences["menu_language"] = new_lang
            update_user_preferences(user_id, preferences)

            # Show confirmation and update menu
            await query.answer(
                f"{MENU_LANGUAGE_OPTIONS[current_lang]} → {MENU_LANGUAGE_OPTIONS[new_lang]}",
                show_alert=True
            )

            # Format the message with the actual language name
            message = get_message("menu_language_set", new_lang)
            formatted_message = message.format(language=MENU_LANGUAGE_OPTIONS[new_lang])
            
            await query.edit_message_text(
                text=formatted_message,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=create_menu_language_selection_keyboard(new_lang, new_lang)
            )
        except Exception as e:
            logger.error(f"Error updating menu language: {e}")
            new_text = get_message("error", language).format(
                error=escape_md("Failed to update language")
            )
            await query.edit_message_text(
                text=new_text, parse_mode=ParseMode.MARKDOWN_V2
            )

# DO NOT REMOVE CONTEXT FROM MENU COMMANDS,
# ITS PASSED BY TELEGRAM HANDLERS 
async def language_menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show menu language selection menu."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(user_id)
        preferences = get_user_preferences(user_id)
        current_lang = preferences.get("menu_language", "en")

        logger.info(f"User {user_id} requested language selection")

        text = get_message("select_language", language)
        markup = create_menu_language_selection_keyboard(language, current_lang)

        # Handle both direct commands and callback queries
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=markup
            )
        else:
            await update.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=markup
            )
    except Exception as e:
        logger.error(f"Error in set language command: {str(e)}", exc_info=True)
        raise