"""Basic command handlers for the bot."""

# Standard library imports
import logging

# Third-party imports
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode


# Local application imports
from src.core.keyboards import create_main_menu_keyboard
from src.core.localization import get_message
from src.core.utils import (
    get_user_language,
    get_user_preferences,
    update_user_preferences,
    toggle_notifications,
)

# Relative imports from handlers package
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
    handle_payment_creation,
    handle_payment_method_selection
)
from .audio import (
    handle_voice_language,
    handle_voice_gender_selection,
    show_voice_language_menu,
)
from .language import handle_menu_language, handle_preferences_language, language_menu_command
from .account import handle_account
from .menu import help_command, about_command, menu_command
from .audio import handle_voice_selection

# Set up module logger
logger = logging.getLogger(__name__)


# DO NOT REMOVE CONTEXT FROM MENU COMMANDS,
# ITS PASSED BY TELEGRAM HANDLERS, EVEN THOUGH ITS NOT USED
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message when the command /start is issued."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(user_id)

        # Log start command
        logger.info(f"User {user_id} started the bot")

        await update.message.reply_text(
            text=get_message("welcome", language),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}", exc_info=True)
        raise


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    try:
        query = update.callback_query
        await query.answer()

        user_id = update.effective_user.id
        language = get_user_language(user_id)
        data = query.data

        logger.info(f"User {user_id} clicked button: {data}")

        # Handle notification toggle
        if data == "toggle_notifications":
            new_state = toggle_notifications(user_id)
            # Update account menu with new notification state
            await handle_account(update, notifications_enabled=new_state)
            return

        # Handle subscription buttons
        if data == "premium":
            await handle_premium(update, context)
            return

        if data in ["subscribe_based", "subscribe_pro", "upgrade_pro"]:
            tier = "pro" if data in ["subscribe_pro", "upgrade_pro"] else "based"
            # Handle payment method selection via payment handler
            await handle_payment_method_selection(update, tier)
            return

        # Handle subscription cancellation flow
        if data == "cancel_subscription_confirm":
            await handle_cancel_subscription_confirm(update)
            return
        elif data == "confirm_cancel_subscription":
            await handle_cancel_subscription(update)
            return
        elif data == "keep_subscription":
            await handle_premium(update, context)
            return
        elif data == "cancel_subscription":
            await handle_cancel_subscription_confirm(update)
            return
        # Handle preferences menu options
        elif data == "preferences":
            await handle_preferences(update)
            return
        # Handle language-related callbacks
        elif data.startswith("set_menu_lang_"):
            await handle_menu_language(update, language, user_id)
            return
        elif data.startswith("set_summary_lang_"):
            await handle_preferences_language(update, language, user_id)
            return
        # Handle payment provider selection
        elif data.startswith("provider_"):
            _, provider, tier = data.split("_")
            await handle_payment_creation(update, provider, tier)
            return
        elif data == "show_summary_language":
            await handle_summary_language(update)
            return
        elif data == "back_to_preferences":
            await handle_preferences(update)
            return
        elif data.startswith("set_length_"):
            length = data.replace("set_length_", "")
            # Make sure length is one of the valid options
            if length in ["short", "medium", "detailed"]:
                await handle_length_setting(update, length)
            return
        elif data == "show_summary_length":
            await handle_length_setting(update)
            return
        elif data == "set_audio_enabled" or data == "set_audio_disabled":
            # Handle audio toggle
            preferences = get_user_preferences(user_id) or {}
            preferences["audio_enabled"] = data == "set_audio_enabled"
            update_user_preferences(user_id, preferences)

            # Refresh audio settings menu
            await handle_audio_settings(update)
            return
        elif data == "set_voice_male":
            await handle_voice_gender_selection(update)
            return
        elif data == "set_voice_female":
            await handle_voice_gender_selection(update)
            return
        elif data.startswith("set_voice_lang_"):
            lang = data.split("_")[-1]
            await handle_voice_language(update, lang)
            return
        elif data == "back_to_menu":
          await menu_command(update, context)
          return
        elif data == "show_support_menu":
            await handle_support_menu(update)
            return
        elif data == "back_to_premium" or data == "premium":
            await handle_premium(update)
            return
        elif data == "help":
            await help_command(update, context)
            return
        elif data == "about":
            await about_command(update, context)
            return
        elif data == "my_account":
            await handle_account(update, context)
            return
        elif data == "show_voice_settings":
            await handle_voice_selection(update)
            return
        elif data.startswith("set_length_"):
            length = data.replace("set_length_", "")
            # Make sure length is one of the valid options
            if length in ["short", "medium", "detailed"]:
                await handle_length_setting(update, length)
            return
        elif data == "lang_menu":
            await language_menu_command(update, context)
            return
        elif data =="voice_language_menu":
            await show_voice_language_menu(update)
            return

        # Default to main menu if no other handler caught the callback
        await query.edit_message_text(
            text=get_message("menu_message", language),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=create_main_menu_keyboard(language)
        )

    except Exception as e:
        logger.error(f"Error in button callback: {str(e)}", exc_info=True)
        raise
