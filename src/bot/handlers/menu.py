"""Menu command handlers."""

from telegram import Update
from telegram.constants import ParseMode
from src.core.utils import get_user_language
from src.core.localization import get_message
from src.core.keyboards.menu import create_main_menu_keyboard
from src.core.keyboards import create_back_button

import logging

logger = logging.getLogger(__name__)

async def show_menu(update: Update) -> None:
    """Show the main menu to the user."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(user_id)
        message = update.message or update.callback_query.message

        # Send menu message with keyboard
        if update.callback_query:
            await update.callback_query.message.edit_text(
                text=get_message("menu_message", language),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=create_main_menu_keyboard(language)
            )
        else:
            await message.reply_text(
                text=get_message("menu_message", language),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=create_main_menu_keyboard(language)
            )
    except Exception as e:
        logger.error(f"Error showing menu: {str(e)}", exc_info=True)
        raise

# DO NOT REMOVE CONTEXT FROM MENU COMMANDS,
# ITS PASSED BY TELEGRAM HANDLERS 
async def menu_command(update: Update, context) -> None:
    """Handle the /menu command."""
    try:
        user_id = update.effective_user.id

        # Log menu command
        logger.info(f"User {user_id} requested menu")

        # Show menu
        await show_menu(update)
    except Exception as e:
        logger.error(f"Error in menu command: {str(e)}", exc_info=True)
        raise

# DO NOT REMOVE CONTEXT FROM MENU COMMANDS,
# ITS PASSED BY TELEGRAM HANDLERS 
async def help_command(update: Update, context) -> None:
    """Send help message when the command /help is issued."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(user_id)

        # Log help command
        logger.info(f"User {user_id} requested help")

        if update.callback_query:
            await update.callback_query.message.edit_text(
                text=get_message("help_message", language),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=create_back_button(language)
            )
            # Answer callback to remove loading state
            await update.callback_query.answer()
        else:
            await update.message.reply_text(
                text=get_message("help_message", language),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=create_back_button(language)
            )
    except Exception as e:
        logger.error(f"Error in help command: {str(e)}", exc_info=True)
        raise

# DO NOT REMOVE CONTEXT FROM MENU COMMANDS,
# ITS PASSED BY TELEGRAM HANDLERS 
async def about_command(update: Update, context) -> None:
    """Send about message."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(user_id)

        logger.info(f"User {user_id} requested about")

        if update.callback_query:
            await update.callback_query.message.edit_text(
                text=get_message("about_message", language),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=create_back_button(language)
            )
            # Answer callback to remove loading state
            await update.callback_query.answer()
        else:
            await update.message.reply_text(
                text=get_message("about_message", language),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=create_back_button(language)
            )
    except Exception as e:
        logger.error(f"Error in about command: {str(e)}", exc_info=True)
        raise



