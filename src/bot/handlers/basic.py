"""Basic command handlers for the bot."""

# Standard library imports
import logging

# Third-party imports
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

# Local application imports
from src.core.keyboards import (
    create_main_menu_keyboard,
    create_language_selection_keyboard,
    create_menu_language_selection_keyboard,
    create_back_button,
    create_payment_method_keyboard,
)
from src.core.localization import get_message
from src.core.utils import get_user_language, get_user_preferences
from src.database.db_manager import db_manager

# Relative imports from handlers package
from .account import handle_account
from .preferences import (
    handle_preferences,
    handle_summary_language,
    handle_audio_settings,
    handle_length_setting,
)
from .premium import (
    handle_premium,
    handle_support_menu,
    handle_cancel_subscription_confirm,
    handle_cancel_subscription,
    handle_payment_creation
)
from .voice import (
    handle_voice_language,
    handle_voice_gender_selection,
    handle_voice_selection,
)
from src.core.utils.text import escape_md
from src.core.keyboards.preferences import MENU_LANGUAGE_OPTIONS

# Set up module logger
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message when the command /start is issued."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)

        # Log start command
        logger.info(f"User {user_id} started the bot")

        await update.message.reply_text(
            text=get_message("welcome", language),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=create_main_menu_keyboard(language),
        )
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}", exc_info=True)
        raise


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show main menu."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)

        logger.info(f"User {user_id} requested main menu")

        await update.message.reply_text(
            text=get_message("menu_message", language),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=create_main_menu_keyboard(language),
        )
    except Exception as e:
        logger.error(f"Error in menu command: {str(e)}", exc_info=True)
        raise


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message when the command /help is issued."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)

        logger.info(f"User {user_id} requested help")

        await update.message.reply_text(
            text=get_message("help_message", language),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=create_back_button(language),
        )
    except Exception as e:
        logger.error(f"Error in help command: {str(e)}", exc_info=True)
        raise


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send about message."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)

        logger.info(f"User {user_id} requested about")

        await update.message.reply_text(
            text=get_message("about_message", language),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=create_back_button(language),
        )
    except Exception as e:
        logger.error(f"Error in about command: {str(e)}", exc_info=True)
        raise


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show menu language selection menu."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)
        preferences = db_manager.get_user_preferences(user_id)
        current_lang = preferences.get("menu_language", "en")

        logger.info(f"User {user_id} requested language selection")

        await update.message.reply_text(
            text=get_message("select_language", language),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=create_menu_language_selection_keyboard(
                language, current_lang
            ),
        )
    except Exception as e:
        logger.error(f"Error in set language command: {str(e)}", exc_info=True)
        raise


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    try:
        query = update.callback_query
        await query.answer()

        user_id = update.effective_user.id
        language = get_user_language(context, user_id)
        data = query.data

        logger.info(f"User {user_id} clicked button: {data}")

        # Get current message text and markup for comparison
        current_text = query.message.text if query.message.text else ""
        current_markup = (
            query.message.reply_markup if query.message.reply_markup else None
        )

        new_text = None
        new_markup = None

        # Handle subscription buttons
        if data in ["subscribe_based", "subscribe_pro", "upgrade_pro"]:
            tier = "pro" if data in ["subscribe_pro", "upgrade_pro"] else "based"
            # Show payment method selection (card/crypto)
            await query.edit_message_text(
                text=get_message("payment_method", language),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=create_payment_method_keyboard(language, tier),
            )
            return

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
        # Handle preferences menu options
        elif data == "preferences":
            await handle_preferences(update, context)
            return
        elif data == "show_summary_length":
            await handle_length_setting(update, context)
            return
        elif data == "show_voice_settings":
            await handle_voice_selection(update, context)
            return
        elif data == "show_voice_language":
            await handle_voice_language(update, context)
            return
        # Handle payment provider selection
        elif data.startswith("provider_"):
            _, provider, tier = data.split("_")
            await handle_payment_creation(update, context, provider, tier)
            return
        elif data == "show_summary_language":
            await handle_summary_language(update, context)
            return
        elif data == "back_to_preferences":
            await handle_preferences(update, context)
            return
        elif data.startswith("set_length_"):
            length = data.replace("set_length_", "")
            await handle_length_setting(update, context, length)
            return
        elif data.startswith("voice_"):
            if "gender" in data:
                await handle_voice_gender_selection(update, context)
            else:
                await handle_voice_language(update, context)
            return
        elif data == "set_audio_enabled" or data == "set_audio_disabled":
            # Get current preferences
            user = db_manager.get_user_data(user_id)
            preferences = user.get("preferences", {})
            # Toggle audio setting
            preferences["audio_enabled"] = data == "set_audio_enabled"
            # Update preferences
            db_manager.update_user_preferences(user_id, preferences)
            # Return to voice settings
            await handle_voice_selection(update, context)
            return
        elif data == "set_voice_male" or data == "set_voice_female":
            await handle_voice_gender_selection(update, context)
            return
        elif data.startswith("set_voice_lang_"):
            lang = data.split("_")[-1]
            await handle_voice_language(update, context, lang)
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
            # Show menu language selection
            preferences = db_manager.get_user_preferences(user_id)
            current_lang = preferences.get("menu_language", "en")
            new_text = get_message("select_language", language)
            new_markup = create_menu_language_selection_keyboard(language, current_lang)
            await query.edit_message_text(
                text=new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
            )
            return
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
                # Update menu language in preferences
                preferences = db_manager.get_user_preferences(user_id)
                preferences["menu_language"] = new_lang
                db_manager.update_user_preferences(user_id, preferences)

                new_text = get_message("language_set", new_lang).format(
                    language=MENU_LANGUAGE_OPTIONS[new_lang]
                )
                new_markup = create_main_menu_keyboard(new_lang)

                await query.edit_message_text(
                    text=new_text,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=new_markup,
                )
            except Exception as e:
                logger.error(f"Error updating language: {e}")
                new_text = get_message("error", language).format(
                    error=escape_md("Failed to update language")
                )
                await query.edit_message_text(
                    text=new_text, parse_mode=ParseMode.MARKDOWN_V2
                )
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
        elif data == "set_length_short":
            length = "short"
            await handle_length_setting(update, context, length)
            return
        elif data == "set_length_long":
            length = "long"
            await handle_length_setting(update, context, length)
            return
        elif data == "set_summary_lang_en":
            lang = "en"
            await handle_summary_language(update, context, lang)
            return
        elif data == "set_summary_lang_ru":
            lang = "ru"
            await handle_summary_language(update, context, lang)
            return
        elif data == "set_voice_lang_en":
            lang = "en"
            await handle_voice_language(update, context, lang)
            return
        elif data == "set_voice_lang_ru":
            lang = "ru"
            await handle_voice_language(update, context, lang)
            return
        elif data == "set_voice_male":
            await handle_voice_gender_selection(update, context)
            return
        elif data == "set_voice_female":
            await handle_voice_gender_selection(update, context)
            return
        elif data == "set_audio_enabled" or data == "set_audio_disabled":
            # Handle audio toggle
            preferences = get_user_preferences(user_id) or {}
            preferences["audio_enabled"] = data == "set_audio_enabled"
            db_manager.update_user_preferences(user_id, preferences)

            # Refresh audio settings menu
            await handle_audio_settings(update, context)
            return

        if new_text and new_markup:
            await query.edit_message_text(
                text=new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
            )

    except Exception as e:
        logger.error(f"Error in button callback: {str(e)}", exc_info=True)
        raise


async def test_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test voice feature."""
    pass  # Implement if needed


async def test_tts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test text-to-speech feature."""
    pass  # Implement if needed
