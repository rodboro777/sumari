"""Account-related command handlers."""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import logging
from datetime import datetime, timezone

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from src.core.keyboards import create_account_keyboard, create_keyboard
from src.core.localization import get_message
from src.database import db_manager
from src.core.utils import get_user_language
from src.config import TIER_LIMITS
from src.core.keyboards.account import ACCOUNT_BUTTONS

logger = logging.getLogger(__name__)


async def handle_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle account-related commands and callbacks."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)

        # Get user data for account info
        user_data = db_manager.get_user_data(user_id)
        premium_status = user_data.get("premium", {})
        tier = premium_status.get("tier", "free")
        is_premium = tier != "free"

        # Get usage data and limits
        usage_data = db_manager.get_monthly_usage(user_id)
        current_usage = usage_data.get("summaries_used", 0)
        summaries_limit = TIER_LIMITS.get(tier, {}).get("summaries_per_month", 5)  # Default to free tier limit
        
        # Format account info message
        account_info = get_message(
            "account_info",
            language,
            username=update.effective_user.username or "Anonymous",
            tier=tier.capitalize(),
            summaries_used=str(current_usage),  # Convert to string for safe formatting
            summaries_limit=str(summaries_limit)  # Convert to string for safe formatting
        )

        # Create keyboard
        keyboard = create_account_keyboard(language, is_premium)

        # Send or edit message
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=account_info,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=keyboard
            )
        else:
            await update.message.reply_text(
                text=account_info,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=keyboard
            )
    except Exception as e:
        logger.error(f"Error in account handler: {str(e)}", exc_info=True)
        error_msg = get_message("error", language, error="Account info unavailable")
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=error_msg,
                parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            await update.effective_message.reply_text(
                text=error_msg,
                parse_mode=ParseMode.MARKDOWN_V2
            )


async def handle_account_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle account settings menu."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)

        # Get user preferences
        preferences = db_manager.get_user_preferences(user_id)
        notifications_enabled = preferences.get("notifications_enabled", True)

        # Format settings message
        settings_info = get_message(
            "account_settings",
            language,
            notifications="✅" if notifications_enabled else "❌"
        )

        # Create keyboard with current settings
        buttons = [
            [
                {
                    "text": get_message("btn_account_notifications", language),
                    "callback_data": ACCOUNT_BUTTONS["notifications"]["callback_data"],
                }
            ],
            [
                {
                    "text": get_message("btn_account_delete", language),
                    "callback_data": ACCOUNT_BUTTONS["delete"]["callback_data"],
                }
            ],
            [
                {
                    "text": get_message("btn_account_back", language),
                    "callback_data": ACCOUNT_BUTTONS["back"]["callback_data"],
                }
            ]
        ]

        # Send or edit message
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=settings_info,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=create_keyboard(buttons, language)
            )
        else:
            await update.message.reply_text(
                text=settings_info,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=create_keyboard(buttons, language)
            )

    except Exception as e:
        logger.error(f"Error in handle_account_settings: {str(e)}", exc_info=True)
        raise
