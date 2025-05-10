"""Message formatting utilities."""
from typing import Optional, Union
from telegram import Message, Update, ReplyKeyboardMarkup, InlineKeyboardMarkup
from telegram.constants import ParseMode
from src.core.localization import get_message
from src.core.utils.text import escape_md

async def send_formatted_message(
    update: Update,
    message_key: str,
    language: str,
    format_args: Optional[dict] = None,
    reply_markup: Optional[Union[ReplyKeyboardMarkup, InlineKeyboardMarkup]] = None,
    delete_after: Optional[int] = None
) -> Message:
    """Send a formatted message with proper escaping and markdown.
    
    Args:
        update: Telegram update object
        message_key: Key for the message in localization
        language: Language code
        format_args: Optional dict of format arguments. Values will be escaped.
        reply_markup: Optional keyboard markup
        delete_after: Optional seconds after which to delete the message
        
    Returns:
        The sent message
    """
    # Get base message
    message = get_message(message_key, language)
    
    # Format with escaped args if provided
    if format_args:
        escaped_args = {k: escape_md(str(v)) for k, v in format_args.items()}
        message = message.format(**escaped_args)
    
    # Send message
    sent_msg = await update.message.reply_text(
        text=message,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=reply_markup
    )
    
    # Delete after delay if requested
    if delete_after:
        await sent_msg.delete(timeout=delete_after)
        
    return sent_msg
