"""Preferences-related command handlers."""

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import logging
import re

from src.core.keyboards import (
    create_preferences_keyboard,
    create_language_selection_keyboard,
    create_summary_length_keyboard,
    create_main_menu_keyboard,
)
from src.core.localization import get_message
from src.database import DatabaseManager
from src.core.utils import get_user_language
from src.core.utils.text import escape_md, format_md
from src.core.utils.decorators import handle_callback_exceptions
from .voice import handle_voice_selection  # Import the voice handler
from src.core.keyboards.preferences import LANGUAGE_OPTIONS, MENU_LANGUAGE_OPTIONS

logger = logging.getLogger(__name__)


async def handle_preferences(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle preferences-related commands and callbacks."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)
        db_manager = DatabaseManager()
        # Get user's premium status
        premium_status = db_manager.get_premium_status(user_id) or {}
        is_pro = premium_status.get("tier", "free") == "pro"

        new_text = get_message("preferences_message", language)
        new_markup = create_preferences_keyboard(language, is_pro)

        if update.callback_query:
            await update.callback_query.edit_message_text(
                new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
            )
        else:
            await update.message.reply_text(
                new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
            )

    except Exception as e:
        logger.error(f"Error in preferences handler: {e}", exc_info=True)
        error_text = get_message("error", language).format(error=escape_md(str(e)))
        if update.callback_query:
            await update.callback_query.edit_message_text(
                error_text, parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            await update.message.reply_text(
                error_text, parse_mode=ParseMode.MARKDOWN_V2
            )


@handle_callback_exceptions
async def handle_summary_language(
    update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str = None
) -> None:
    """Handle summary language selection."""
    db_manager = DatabaseManager()
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)
        if lang:
            # Update user preferences with new language

            preferences = db_manager.get_user_preferences(user_id) or {}
            old_lang = preferences.get("summary_language", "en")
            preferences["summary_language"] = lang
            db_manager.update_user_preferences(user_id, preferences)

            # Show confirmation message with language names
            old_name = LANGUAGE_OPTIONS[old_lang]
            new_name = LANGUAGE_OPTIONS[lang]
            await update.callback_query.answer(
                f"{old_name} → {new_name}",
                show_alert=True,
            )

            # Update menu with new selection
            new_text = (
                get_message("select_summary_language", language)
                + "\n\n"
                + get_message("language_changed", language).format(
                    language=escape_md(LANGUAGE_OPTIONS[lang])
                )
            )
            new_markup = create_language_selection_keyboard(
                language, source="preferences", current_lang=lang
            )

            await update.callback_query.edit_message_text(
                new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
            )
            return

        # Show language selection menu with current selection
        preferences = db_manager.get_user_preferences(user_id) or {}
        current_lang = preferences.get("summary_language", "en")
        new_text = get_message("select_summary_language", language)
        new_markup = create_language_selection_keyboard(
            language, source="preferences", current_lang=current_lang
        )

        await update.callback_query.edit_message_text(
            new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
        )

    except Exception as e:
        logger.error(f"Error in summary language handler: {e}", exc_info=True)
        error_text = get_message("error", language).format(error=escape_md(str(e)))
        await update.callback_query.edit_message_text(
            error_text, parse_mode=ParseMode.MARKDOWN_V2
        )


@handle_callback_exceptions
async def handle_menu_language_change(
    update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str = None
) -> None:
    """Handle menu language selection."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)
        db_manager = DatabaseManager()

        if lang:
            # Get current preferences
            preferences = db_manager.get_user_preferences(user_id)
            old_lang = preferences.get("menu_language", "en")

            # Update menu language in preferences
            preferences["menu_language"] = lang
            preferences["summary_language"] = lang
            db_manager.update_user_preferences(user_id, preferences)

            # Show confirmation message
            old_name = MENU_LANGUAGE_OPTIONS[old_lang]
            new_name = MENU_LANGUAGE_OPTIONS[lang]
            await update.callback_query.answer(
                f"{old_name} → {new_name}",
                show_alert=True,
            )

            # Return to main menu with new language
            new_text = get_message("menu_message", lang)
            new_markup = create_main_menu_keyboard(lang)

            await update.callback_query.edit_message_text(
                text=new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
            )
            return

        # Show language selection menu
        preferences = db_manager.get_user_preferences(user_id)
        current_lang = preferences.get("menu_language", "en")
        new_text = get_message("select_language", language)
        new_markup = create_main_menu_keyboard(language, current_lang)

        await update.callback_query.edit_message_text(
            text=new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
        )

    except Exception as e:
        logger.error(f"Error in menu language handler: {e}", exc_info=True)
        error_text = get_message("error", language).format(error=escape_md(str(e)))
        await update.callback_query.edit_message_text(
            error_text, parse_mode=ParseMode.MARKDOWN_V2
        )


async def handle_audio_settings(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Route to voice selection handler."""
    await handle_voice_selection(update, context)


@handle_callback_exceptions
async def handle_length_setting(
    update: Update, context: ContextTypes.DEFAULT_TYPE, length: str = None
) -> None:
    """Handle summary length setting."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)
        if length:
            # Update length preference
            db_manager = DatabaseManager()
            preferences = db_manager.get_user_preferences(user_id) or {}
            old_length = preferences.get("summary_length", "medium")
            preferences["summary_length"] = length
            db_manager.update_user_preferences(user_id, preferences)

            # Show confirmation and update menu
            length_names = {
                "short": get_message("btn_summary_short", language),
                "medium": get_message("btn_summary_medium", language),
                "detailed": get_message("btn_summary_detailed", language),
            }

            await update.callback_query.answer(
                f"{length_names[old_length]} → {length_names[length]}",
                show_alert=True,
            )

            # Update menu with new selection
            new_text = (
                get_message("summary_preferences", language)
                + "\n\n"
                + get_message("length_changed", language).format(
                    length=escape_md(length_names[length])
                )
            )
            new_markup = create_summary_length_keyboard(language, current_length=length)

            await update.callback_query.edit_message_text(
                new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
            )
            return

        # Show length selection menu with current selection
        preferences = db_manager.get_user_preferences(user_id) or {}
        current_length = preferences.get("summary_length", "medium")
        new_text = get_message("summary_preferences", language)
        new_markup = create_summary_length_keyboard(
            language, current_length=current_length
        )

        await update.callback_query.edit_message_text(
            new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
        )

    except Exception as e:
        logger.error(f"Error updating preferences: {e}", exc_info=True)
        error_text = get_message("error", language).format(error=escape_md(str(e)))
        await update.callback_query.edit_message_text(
            error_text, parse_mode=ParseMode.MARKDOWN_V2
        )
