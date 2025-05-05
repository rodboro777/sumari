"""Utility decorators for error handling."""

import logging
from functools import wraps
from telegram import Update
from telegram.constants import ParseMode
from src.core.localization import get_message

logger = logging.getLogger(__name__)


def handle_callback_exceptions(func):
    """Decorator to handle exceptions in callback handlers."""

    @wraps(func)
    async def wrapper(update: Update, context, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            if update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(
                    get_message("error", "en", error=str(e)),
                    parse_mode=ParseMode.MARKDOWN_V2,
                )

    return wrapper
