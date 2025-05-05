"""Voice-related message handlers."""

from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode
import logging

from src.core.keyboards import (
    create_voice_selection_keyboard,
    create_voice_language_keyboard,
    create_premium_options_keyboard,
)
from src.database.db_manager import db_manager
from src.core.utils.decorators import handle_callback_exceptions
from src.core.localization import get_message
from src.core.keyboards.preferences import LANGUAGE_OPTIONS

logger = logging.getLogger(__name__)


@handle_callback_exceptions
async def handle_voice_selection(update: Update, context: CallbackContext) -> None:
    """Handle voice selection menu."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = db_manager.get_user_data(user_id)
    language = user.get("language", "en")

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
    preferences = user.get("preferences", {})
    audio_enabled = preferences.get("audio_enabled", False)
    current_gender = preferences.get("voice_gender", "female")
    voice_language = preferences.get("voice_language", "en")

    # Build status message
    status_message = (
        get_message("voice_selection", language)
        + "\n• "
        + get_message("audio_" + ("enabled" if audio_enabled else "disabled"), language)
        + "\n• "
        + (
            "👨 Male Voice"
            if current_gender == "male"
            else (
                "👩 Female Voice"
                if language == "en"
                else (
                    "👨 Мужской голос"
                    if current_gender == "male"
                    else "👩 Женский голос"
                )
            )
        )
    )

    # Create keyboard with current settings
    keyboard = create_voice_selection_keyboard(
        language=language, audio_enabled=audio_enabled, current_gender=current_gender
    )

    # Update message with audio settings
    await query.edit_message_text(
        status_message,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=keyboard,
    )


@handle_callback_exceptions
async def handle_voice_language(
    update: Update, context: CallbackContext, lang: str = None
) -> None:
    """Handle voice language selection."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = db_manager.get_user_data(user_id)
    language = user.get("language", "en")

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
        preferences = user.get("preferences", {})
        old_language = preferences.get("voice_language", "en")
        preferences["voice_language"] = lang
        db_manager.update_user_preferences(user_id, preferences)

        # Show confirmation message with language names
        old_name = LANGUAGE_OPTIONS[old_language]["text"][language]
        new_name = LANGUAGE_OPTIONS[lang]["text"][language]
        await query.answer(
            (
                f"🌐 {old_name} → {new_name}"
                if language == "en"
                else f"🌐 {old_name} → {new_name}"
            ),
            show_alert=True,
        )

        # Return to audio settings
        await handle_voice_selection(update, context)
        return

    # Show language selection menu
    await query.edit_message_text(
        get_message("voice_language", language),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=create_voice_language_keyboard(language),
    )


@handle_callback_exceptions
async def handle_voice_gender_selection(
    update: Update, context: CallbackContext
) -> None:
    """Handle voice gender selection."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = db_manager.get_user_data(user_id)
    language = user.get("language", "en")

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

    preferences = user.get("preferences", {})

    # Toggle gender selection
    new_gender = "male" if query.data == "set_voice_male" else "female"
    preferences["voice_gender"] = new_gender

    # Update user preferences
    db_manager.update_user_preferences(user_id, preferences)

    # Show confirmation message
    confirmation = (
        "👨 Voice set to male!"
        if new_gender == "male"
        else (
            "👩 Voice set to female!"
            if language == "en"
            else (
                "👨 Установлен мужской голос!"
                if new_gender == "male"
                else "👩 Установлен женский голос!"
            )
        )
    )
    await query.answer(confirmation, show_alert=True)

    # Return to audio settings with updated preferences
    await handle_voice_selection(update, context)
