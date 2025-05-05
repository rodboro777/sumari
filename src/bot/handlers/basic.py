"""Basic command handlers for the bot."""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import logging
import re

from src.core.keyboards import (
    create_main_menu_keyboard,
    create_language_selection_keyboard,
    create_back_button,
)
from src.core.keyboards.premium import create_support_menu_keyboard
from src.core.localization import get_message
from src.database.db_manager import db_manager
from src.bot.utils import get_user_language
from .modules import (
    handle_account,
    handle_preferences,
    handle_summary_language,
    handle_audio_settings,
    handle_length_setting,
    handle_premium,
    handle_cancel_subscription_confirm,
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message when the command /start is issued."""
    try:
        user_id = update.effective_user.id
        
        # Initialize user in database if needed
        db_manager.add_user(user_id)

        # Get user's language preference
        language = get_user_language(context, user_id)
        
        # Send welcome message
        await update.message.reply_text(
            get_message("welcome", language),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=create_main_menu_keyboard(language),
        )
    except Exception as e:
        logger.error(f"Error in start command: {e}", exc_info=True)
        await update.message.reply_text(
            get_message("error", "en", error=str(e)), parse_mode=ParseMode.MARKDOWN_V2
        )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show main menu."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)
        
        await update.message.reply_text(
            get_message("menu_message", language),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=create_main_menu_keyboard(language),
        )
    except Exception as e:
        logger.error(f"Error in menu command: {e}", exc_info=True)
        await update.message.reply_text(
            get_message("error", language, error=str(e)),
            parse_mode=ParseMode.MARKDOWN_V2,
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message when the command /help is issued."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)
        
        await update.message.reply_text(
            get_message("help_message", language),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=create_back_button(language),
        )
    except Exception as e:
        logger.error(f"Error in help command: {e}", exc_info=True)
        await update.message.reply_text(
            get_message("error", language, error=str(e)),
            parse_mode=ParseMode.MARKDOWN_V2,
        )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send about message."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)
        
        await update.message.reply_text(
            get_message("about_message", language),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=create_back_button(language),
        )
    except Exception as e:
        logger.error(f"Error in about command: {e}", exc_info=True)
        await update.message.reply_text(
            get_message("error", language, error=str(e)),
            parse_mode=ParseMode.MARKDOWN_V2,
        )


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show language selection menu."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)
        
        await update.message.reply_text(
            get_message("select_language", language),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=create_language_selection_keyboard(language),
        )
    except Exception as e:
        logger.error(f"Error in set language command: {e}", exc_info=True)
        await update.message.reply_text(
            get_message("error", language, error=str(e)),
            parse_mode=ParseMode.MARKDOWN_V2,
        )


def escape_markdown_v2(text: str) -> str:
    """Escape Telegram MarkdownV2 special characters."""
    # Place - at the end, and escape the backslash itself
    to_escape = r"_\*\[\]()~`>#+=|{}.!\\-"
    return re.sub(f"([{to_escape}])", r"\\\1", text)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)
        data = query.data
        
        # Get current message text and markup for comparison
        current_text = query.message.text if query.message.text else ""
        current_markup = (
            query.message.reply_markup if query.message.reply_markup else None
        )
        
        new_text = None
        new_markup = None
        
        # Handle subscription cancellation flow
        if data == "cancel_subscription_confirm":
            await handle_cancel_subscription_confirm(update, context)
            return
        elif data == "confirm_cancel_subscription":
            await handle_cancel_subscription(update, context)
            return
        elif data == "keep_subscription":
            await handle_premium(update, context)
            return
        elif data == "cancel_subscription":
            await handle_cancel_subscription_confirm(update, context)
            return

        if data == "back_to_menu":
            new_text = get_message("menu_message", language)
            new_markup = create_main_menu_keyboard(language)
        elif data == "show_support_menu":
            await handle_support_menu(update, context)
            return
        elif data == "back_to_premium" or data == "premium":
            await handle_premium(update, context)
            return
        elif data == "lang_menu":
            # Store the source of language menu access in user_data
            context.user_data["lang_menu_source"] = "main_menu"
            new_text = get_message("select_language", language)
            new_markup = create_language_selection_keyboard(
                language, source="main_menu"
            )
        elif data == "show_language_from_prefs":
            # Store the source of language menu access in user_data
            context.user_data["lang_menu_source"] = "preferences"
            new_text = get_message("select_language", language)
            new_markup = create_language_selection_keyboard(
                language, source="preferences"
            )
        elif data.startswith("lang_"):
            new_lang = data.split("_")[1]
            try:
                db_manager.update_user_language(user_id, new_lang)
                message = get_message(
                    "language_set",
                    new_lang,
                    language="English" if new_lang == "en" else "Русский",
                )
                new_text = message

                # Check where to return after language selection
                lang_menu_source = context.user_data.get(
                    "lang_menu_source", "main_menu"
                )
                if lang_menu_source == "preferences":
                    await handle_preferences(update, context)
                    return
                new_markup = create_main_menu_keyboard(new_lang)
            except Exception as e:
                logger.error(f"Error updating language: {e}")
                new_text = get_message(
                    "error", language, error="Failed to update language"
                )
        elif data == "preferences":
            await handle_preferences(update, context)
            return
        elif data == "help":
            new_text = get_message("help_message", language)
            new_markup = create_back_button(language)
        elif data == "about":
            new_text = get_message("about_message", language)
            new_markup = create_back_button(language)
        elif data == "my_account":
            await handle_account(update, context)
            return
        elif data == "show_length_options":
            await handle_length_setting(update, context)
            return
        elif data == "show_summary_language":
            await handle_summary_language(update, context)
            return
        elif data == "show_voice_language":
            await handle_voice_language(update, context)
            return
        elif data == "audio_settings":
            await handle_audio_settings(update, context)
            return
        elif data == "back_to_preferences":
            await handle_preferences(update, context)
            return
        elif data.startswith("set_length_"):
            length = data.split("_")[2]  # set_length_short -> short
            await handle_length_setting(update, context, length)
            return
        elif data.startswith("set_summary_lang_"):
            lang = data.split("_")[-1]  # set_summary_lang_en -> en
            await handle_summary_language(update, context, lang)
            return
        elif data.startswith("set_voice_lang_"):
            lang = data.split("_")[-1]  # set_voice_lang_en -> en
            await handle_voice_language(update, context, lang)
            return
        elif data.startswith("set_voice_"):
            await handle_voice_gender_selection(update, context)
            return
        elif data == "set_audio_enabled" or data == "set_audio_disabled":
            # Handle audio toggle
            preferences = db_manager.get_user_preferences(user_id) or {}
            preferences["audio_enabled"] = data == "set_audio_enabled"
            db_manager.update_user_preferences(user_id, preferences)

            # Refresh audio settings menu
            await handle_audio_settings(update, context)
            return

        if new_text and new_markup:
            await query.edit_message_text(
                new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
            )
            
    except Exception as e:
        logger.error(f"Error in button callback: {e}", exc_info=True)
        try:
            error_text = get_message("error", language, error=str(e))
            await query.edit_message_text(error_text, parse_mode=ParseMode.MARKDOWN_V2)
        except Exception as e2:
            logger.error(f"Error sending error message: {e2}", exc_info=True)


# Add test_voice and test_tts functions if needed
async def test_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test voice feature."""
    pass  # Implement if needed


async def test_tts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test text-to-speech feature."""
    pass  # Implement if needed
