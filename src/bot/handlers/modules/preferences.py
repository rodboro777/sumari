"""Preferences-related command handlers."""

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import logging

from src.core.keyboards import (
    create_preferences_keyboard,
    create_language_selection_keyboard,
    create_length_selection_keyboard,
    create_premium_options_keyboard,
    create_back_button,
)
from src.core.localization import get_message
from src.database.db_manager import db_manager
from src.bot.utils import get_user_language, get_user_preferences
from src.core.utils.decorators import handle_callback_exceptions
from .voice import handle_voice_selection  # Import the voice handler

logger = logging.getLogger(__name__)


async def handle_preferences(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle preferences-related commands and callbacks."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)

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
        error_text = get_message("error", language).format(error=str(e))
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
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)

        if lang:
            # Update user preferences with new language
            preferences = db_manager.get_user_preferences(user_id) or {}
            preferences["summary_language"] = lang
            db_manager.update_user_preferences(user_id, preferences)

            # Return to preferences menu
            await handle_preferences(update, context)
            return

        # Show language selection menu
        new_text = get_message("select_summary_language", language)
        new_markup = create_language_selection_keyboard(
            language, setting_type="summary"
        )

        await update.callback_query.edit_message_text(
            new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
        )

    except Exception as e:
        logger.error(f"Error in summary language handler: {e}", exc_info=True)
        error_text = get_message("error", language).format(error=str(e))
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
            preferences = db_manager.get_user_preferences(user_id) or {}
            preferences["summary_length"] = length
            db_manager.update_user_preferences(user_id, preferences)

            # Return to preferences menu
            await handle_preferences(update, context)
            return

        # Show length selection menu
        new_text = get_message("summary_preferences", language).replace("*", "\\*")
        new_markup = create_length_selection_keyboard(language)

        await update.callback_query.edit_message_text(
            new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
        )

    except Exception as e:
        logger.error(f"Error updating preferences: {e}", exc_info=True)
        error_text = get_message("error", language).format(error=str(e))
        await update.callback_query.edit_message_text(
            error_text, parse_mode=ParseMode.MARKDOWN_V2
        )
