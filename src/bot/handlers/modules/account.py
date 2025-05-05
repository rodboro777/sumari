"""Account-related command handlers."""

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import logging

from src.core.keyboards import create_account_keyboard
from src.core.localization import get_message
from src.database.db_manager import db_manager
from src.bot.utils import get_user_language

logger = logging.getLogger(__name__)


async def handle_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle account-related commands and callbacks."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)

        # Get user data for account info
        user_data = db_manager.get_user_data(user_id)
        premium_status = user_data.get("premium", {})
        is_premium = premium_status.get("tier", "free") != "free"

        # Create account info message
        account_info = get_message("account_info", language).format(
            username=update.effective_user.username or "Anonymous",
            tier=premium_status.get("tier", "free"),
            summaries_used=premium_status.get("summaries_used", 0),
            summaries_limit=premium_status.get("summaries_limit", 3),
        )

        # Send or edit message
        if update.callback_query:
            await update.callback_query.edit_message_text(
                account_info,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=create_account_keyboard(language, has_premium=is_premium),
            )
        else:
            await update.message.reply_text(
                account_info,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=create_account_keyboard(language, has_premium=is_premium),
            )

    except Exception as e:
        logger.error(f"Error in account handler: {e}", exc_info=True)
        error_text = get_message("error", language).format(error=str(e))
        if update.callback_query:
            await update.callback_query.edit_message_text(
                error_text, parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            await update.message.reply_text(
                error_text, parse_mode=ParseMode.MARKDOWN_V2
            )
