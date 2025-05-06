"""Audio summary related handlers."""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import logging

from src.core.localization import get_message
from src.core.utils.decorators import handle_callback_exceptions
from src.database.db_manager import db_manager

logger = logging.getLogger(__name__)

@handle_callback_exceptions
async def handle_audio_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle request for audio version of summary."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user = db_manager.get_user_data(user_id)
    language = user.get("language", "en")
    
    # Check if user is pro
    premium_status = user.get("premium", {})
    is_pro = premium_status.get("tier", "free") == "pro"
    
    if not is_pro:
        await query.message.reply_text(
            get_message("premium_only_feature", language),
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return
    
    # Get audio_processor from bot_data
    audio_processor = context.bot_data.get("audio_processor")
    if not audio_processor:
        logger.error("Audio processor not found in bot_data")
        await query.message.reply_text(
            get_message("error_occurred", language),
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return
    
    # Get the summary text from the original message
    summary_text = query.message.text
    if not summary_text:
        await query.message.reply_text(
            get_message("no_summary_found", language),
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return
        
    # Get user voice preferences
    preferences = user.get("preferences", {})
    voice_gender = preferences.get("voice_gender", "female")
    voice_language = preferences.get("voice_language", language)
    
    # Map preferences to voice ID
    voice_map = {
        "en": {"male": "en-US-Standard-D", "female": "en-US-Standard-F"},
        "es": {"male": "es-ES-Standard-C", "female": "es-ES-Standard-D"},
        "pt": {"male": "pt-BR-Standard-B", "female": "pt-BR-Standard-C"},
        "hi": {"male": "hi-IN-Standard-B", "female": "hi-IN-Standard-A"},
        "ru": {"male": "ru-RU-Standard-D", "female": "ru-RU-Standard-E"}
    }
    
    voice = voice_map.get(voice_language, {}).get(voice_gender, "en-US-Standard-F")
    
    # Show processing message
    processing_message = await query.message.reply_text(
        get_message("generating_audio", language),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    
    try:
        # Generate audio summary
        success, result = await audio_processor.generate_audio_summary(
            text=summary_text,
            voice=voice,
            user_id=user_id
        )
        
        if not success:
            error_msg = result.get("error", "Unknown error")
            await processing_message.edit_text(
                get_message("audio_generation_failed", language).format(error=error_msg),
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return
            
        # Send audio file
        audio_url = result.get("audio_url")
        if audio_url:
            await processing_message.edit_text(
                get_message("audio_ready", language),
                parse_mode=ParseMode.MARKDOWN_V2
            )
            await context.bot.send_audio(
                chat_id=user_id,
                audio=audio_url,
                caption=get_message("audio_summary_caption", language),
                parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            await processing_message.edit_text(
                get_message("audio_url_missing", language),
                parse_mode=ParseMode.MARKDOWN_V2
            )
            
    except Exception as e:
        logger.error(f"Error generating audio summary: {str(e)}", exc_info=True)
        await processing_message.edit_text(
            get_message("error", language).format(error=str(e)),
            parse_mode=ParseMode.MARKDOWN_V2
        )
