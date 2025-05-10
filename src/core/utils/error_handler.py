"""Error handling utilities for the bot."""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import logging
from src.logging import metrics_collector
from src.core.utils import get_user_language
from src.core.localization import get_message
from src.core.utils.text import escape_md

logger = logging.getLogger(__name__)

def format_error_message(error: Exception) -> str:
    """Format error message for user.
    
    Args:
        error: The error exception
        
    Returns:
        Formatted error message
    """
    if isinstance(error, Exception):
        return str(error)
    return "An unknown error occurred"

async def handle_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer.
    
    Args:
        update: The update that caused the error
        context: The context of the error
    """
    # Log the error
    logger.error("Exception while handling an update:", exc_info=context.error)

    # Get error message
    error_msg = format_error_message(context.error)

    # Log to monitoring service
    metrics_collector.log_error("telegram_bot", error_msg)

    # Send message to user if possible
    if update and isinstance(update, Update) and update.effective_chat:
        language = get_user_language( update.effective_user.id)
        error_text = escape_md(get_message("error", language).format(error=error_msg))
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=error_text,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
