"""Preferences-related command handlers."""

from telegram import Update
from telegram.constants import ParseMode
import logging
from src.core.keyboards import (
    create_preferences_keyboard,
    create_language_selection_keyboard,
    create_summary_length_keyboard,
)
from src.core.localization import get_message
from src.core.utils import (
    get_user_language,
    get_user_preferences,
    update_user_preferences,
    get_user_data,
)
from src.services.payments.payment_processor import PaymentProcessor
from src.core.utils.text import escape_md
from src.core.utils.decorators import handle_callback_exceptions
from .audio import handle_voice_selection  
from src.core.utils.language_config import LANGUAGE_OPTIONS, MENU_LANGUAGE_OPTIONS

logger = logging.getLogger(__name__)


async def handle_preferences(update: Update) -> None:
    """Handle preferences menu."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(user_id)

        # Get current preferences
        preferences = get_user_preferences(user_id)

        # Create preferences message
        message = get_message("preferences_message", language)
        user = get_user_data(user_id)
        premium_status = user.get("premium", {})
        is_pro = premium_status.get("tier", "free") == "pro"

        # Create preferences keyboard
        markup = create_preferences_keyboard(language, is_pro)

        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=message, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=markup
            )
        else:
            await update.message.reply_text(
                text=message, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=markup
            )
    except Exception as e:
        logger.error(f"Error in preferences handler: {e}")
        error_text = get_message("error", language).format(error=str(e))
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=error_text, parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            await update.message.reply_text(
                text=error_text, parse_mode=ParseMode.MARKDOWN_V2
            )

# Opens language selection menu for summary language 
@handle_callback_exceptions
async def handle_summary_language(update: Update, lang: str = None) -> None:
    """Handle summary language selection."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(user_id)
        if lang:
            # Update user preferences with new language

            preferences = get_user_preferences(user_id)
            old_lang = preferences.get("summary_language", "en")
            preferences["summary_language"] = lang
            update_user_preferences(user_id, preferences)

            # Show confirmation message with language names
            old_name = LANGUAGE_OPTIONS[old_lang]
            new_name = LANGUAGE_OPTIONS[lang]
            await update.callback_query.answer(
                f"{old_name} → {new_name}",
                show_alert=True,
            )

            # Update menu with new selection
            new_text = (
                get_message("select_summary_language", language)
                + "\n\n"
                + get_message("language_changed", language).format(
                    language=escape_md(LANGUAGE_OPTIONS[lang])
                )
            )
            new_markup = create_language_selection_keyboard(
                language, source="preferences", current_lang=lang
            )

            await update.callback_query.edit_message_text(
                new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
            )
            return

        # Show language selection menu with current selection
        preferences = get_user_preferences(user_id)
        current_lang = preferences.get("summary_language", "en")
        new_text = get_message("select_summary_language", language)
        new_markup = create_language_selection_keyboard(
            language, source="preferences", current_lang=current_lang
        )

        await update.callback_query.edit_message_text(
            new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
        )

    except Exception as e:
        logger.error(f"Error in summary language handler: {e}", exc_info=True)
        error_text = get_message("error", language).format(error=escape_md(str(e)))
        await update.callback_query.edit_message_text(
            error_text, parse_mode=ParseMode.MARKDOWN_V2
        )


async def handle_audio_settings(
    update: Update,
) -> None:
    """Route to voice selection handler."""
    await handle_voice_selection(update)


@handle_callback_exceptions
async def handle_length_setting(update: Update, length: str = None) -> None:
    """Handle summary length setting."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(user_id)
        preferences = get_user_preferences(user_id)
        current_length = preferences.get("summary_length", "medium")

        if length:
            # Don't do anything if the length hasn't changed
            if length == current_length:
                await update.callback_query.answer(
                    get_message("already_selected", language),
                    show_alert=True
                )
                return

            # Update length preference
            preferences["summary_length"] = length
            update_user_preferences(user_id, preferences)

            # Show confirmation and update menu
            length_names = {
                "short": get_message("btn_summary_short", language),
                "medium": get_message("btn_summary_medium", language),
                "detailed": get_message("btn_summary_detailed", language),
            }

            await update.callback_query.answer(
                f"{length_names[current_length]} → {length_names[length]}",
                show_alert=True,
            )

            # Update menu with new selection
            new_text = (
                get_message("summary_preferences", language)
                + "\n\n"
                + get_message("length_changed", language).format(
                    length=escape_md(length_names[length])
                )
            )
            new_markup = create_summary_length_keyboard(language, current_length=length)

            await update.callback_query.edit_message_text(
                new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
            )
            return

        # Show length selection menu with current selection
        new_text = get_message("summary_preferences", language)
        new_markup = create_summary_length_keyboard(
            language, current_length=current_length
        )

        await update.callback_query.edit_message_text(
            new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
        )

    except Exception as e:
        logger.error(f"Error updating preferences: {e}", exc_info=True)
        error_text = get_message("error", language).format(error=escape_md(str(e)))
        await update.callback_query.edit_message_text(
            error_text, parse_mode=ParseMode.MARKDOWN_V2
        )


async def successful_payment_callback(update: Update) -> None:
    """Handle successful payments."""
    try:
        user_id = update.effective_user.id
        user_lang = get_user_language(user_id)
        payment = update.message.successful_payment
        tier = payment.invoice_payload.split("_")[1]

        # Process the payment
        await PaymentProcessor().process_successful_payment(
            user_id, payment.total_amount, tier
        )

        # Send confirmation message
        await update.message.reply_text(
            get_message("payment_success", user_lang), parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Error in successful payment: {str(e)}", exc_info=True)
        await update.message.reply_text(
            get_message("payment_error", user_lang).format(str(e)),
            parse_mode="Markdown",
        )

