"""Voice-related message handlers."""

from telegram import Update
from telegram.constants import ParseMode
import logging

from src.core.keyboards import (
    create_voice_selection_keyboard,
    create_voice_language_keyboard,
    create_premium_options_keyboard,
)
from src.core.utils.decorators import handle_callback_exceptions
from src.core.localization import get_message
from src.core.utils import (
    get_user_preferences, 
    get_user_data,
    update_user_preferences
)
from src.core.utils.text import escape_md
from src.core.utils.language_config import LANGUAGE_OPTIONS
from telegram.ext import ContextTypes
logger = logging.getLogger(__name__)


@handle_callback_exceptions
async def handle_voice_selection(update: Update) -> None:
    """Handle voice selection menu."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user_data(user_id)
    language = user.get("language", "en")
    preferences = get_user_preferences(user_id)

    # Check if user is pro
    premium_status = user.get("premium", {})
    is_pro = premium_status.get("tier", "free") == "pro"

    if not is_pro:
        # Show premium upgrade prompt
        await query.edit_message_text(
            get_message("premium_features", language),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=create_premium_options_keyboard(language),
            
        )
        return

    # Get current audio settings
    audio_enabled = preferences.get("audio_enabled", False)
    current_gender = preferences.get("voice_gender", "female")
    voice_language = preferences.get("voice_language", "en")

    # Get localized status messages
    audio_status = get_message(
        "audio_enabled" if audio_enabled else "audio_disabled", language)
    voice_gender = current_gender.capitalize()
    voice_language_name = LANGUAGE_OPTIONS.get(voice_language, voice_language)

    # Get message template - no need to escape it as it's already escaped in localization
    status_message = get_message("voice_selection", language)

    # Create keyboard with current settings
    keyboard = create_voice_selection_keyboard(
        language=language, audio_enabled=audio_enabled, current_gender=current_gender
    )

    # Update message with audio settings
    await query.edit_message_text(
        status_message.format(
            audio_status=audio_status,
            voice_gender=voice_gender,
            voice_language=voice_language_name,
        ),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=keyboard,
    )


@handle_callback_exceptions
async def handle_voice_language(
    update: Update, lang: str = None
) -> None:
    """Handle voice language selection."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user_data(user_id)
    language = user.get("language", "en")
    preferences = get_user_preferences(user_id)

    # Check if user is pro
    premium_status = user.get("premium", {})
    is_pro = premium_status.get("tier", "free") == "pro"

    if not is_pro:
        # Show premium upgrade prompt
        await query.edit_message_text(
            get_message("premium_features", language),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=create_premium_options_keyboard(language),
        )
        return

    if lang:
        # Update voice language preference
        old_language = preferences.get("voice_language", "en")
        preferences["voice_language"] = lang
        update_user_preferences(user_id, preferences)

        # Show confirmation message with language names
        old_name = LANGUAGE_OPTIONS[old_language]
        new_name = LANGUAGE_OPTIONS[lang]
        await query.answer(
             f"{old_name} → {new_name}",
             parse_mode=ParseMode.MARKDOWN_V2,
            show_alert=True,
        )

        # Return to audio settings
        await handle_voice_selection(update)
        return

    # Show language selection menu
    await show_voice_language_menu(update)


@handle_callback_exceptions
async def show_voice_language_menu(update: Update) -> None:
    """Show voice language selection menu."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user_data(user_id)
    language = user.get("language", "en")
    preferences = get_user_preferences(user_id)

    lang = get_message("voice_language", language)
    
    
    # Show language selection menu
    keyboard = create_voice_language_keyboard(language)
    await query.edit_message_text(
        lang,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=keyboard,
        
    )


@handle_callback_exceptions
async def handle_voice_gender_selection(
    update: Update
) -> None:
    """Handle voice gender selection."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = get_user_data(user_id)
    language = user.get("language", "en")
    preferences = get_user_preferences(user_id)

    # Check if user is pro
    premium_status = user.get("premium", {})
    is_pro = premium_status.get("tier", "free") == "pro"

    if not is_pro:
        # Show premium upgrade prompt
        await query.edit_message_text(
            get_message("premium_features", language),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=create_premium_options_keyboard(language),
        )
        return

    # Toggle gender selection
    new_gender = "male" if query.data == "set_voice_male" else "female"
    preferences["voice_gender"] = new_gender

    # Update user preferences
    update_user_preferences(user_id, preferences)

    # Show confirmation message
    confirmation = get_message(f"voice_{new_gender}_set", language)
    await query.answer(confirmation, show_alert=True)

    # Return to audio settings with updated preferences
    await handle_voice_selection(update)

logger = logging.getLogger(__name__)

@handle_callback_exceptions
async def handle_audio_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle request for audio version of summary."""
    query = update.callback_query
    await query.answer()
    audio_processor = AudioProcessor()
    user_id = update.effective_user.id
    user = get_user_data(user_id)
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
