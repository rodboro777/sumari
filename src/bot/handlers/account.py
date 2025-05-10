"""Account-related command handlers."""

from telegram import Update
from telegram.constants import ParseMode
import logging

from telegram import Update
from telegram.constants import ParseMode

from src.core.keyboards import create_account_keyboard
from src.core.localization import get_message
from src.core.utils import (
    get_user_language,
    get_user_data,
    get_monthly_usage,
    update_user_preferences
)
from src.config import TIER_LIMITS

logger = logging.getLogger(__name__)


async def handle_account(update: Update, notifications_enabled: bool = None) -> None:
    """Handle account-related commands and callbacks."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(user_id)

        # Get user data for account info
        user_data = get_user_data(user_id)
        premium_status = user_data.get("premium", {})
        tier = premium_status.get("tier", "free")
        is_premium = tier != "free"

        # Get current notifications status before any changes
        preferences = user_data.get("preferences", {})
        
        # Use new notification status immediately for UI if provided
        current_notifications = notifications_enabled if notifications_enabled is not None else preferences.get("notifications_enabled", True)

        # Get usage data and limits
        usage_data = get_monthly_usage(user_id)
        current_usage = usage_data.get("summaries_used", 0)
        summaries_limit = TIER_LIMITS.get(tier, {}).get(
            "monthly_summaries", 5
        )  # Default to free tier limit

        # Format account info message
        account_info = get_message(
            "account_info",
            language,
            username=update.effective_user.username or "Anonymous",
            tier=tier.capitalize(),
            summaries_used=str(current_usage),
            summaries_limit=str(summaries_limit),
            notifications="✅" if current_notifications else "❌",
        )

        # Create keyboard with current notification status
        keyboard = create_account_keyboard(language, is_premium, current_notifications)
        
        # Update UI first
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=account_info,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=keyboard,
            )
        else:
            await update.message.reply_text(
                text=account_info,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=keyboard,
            )

        # Then update the database if needed
        if notifications_enabled is not None:
            # Update preferences directly
            update_user_preferences(user_id, {"notifications_enabled": notifications_enabled})


    except Exception as e:
        logger.error(f"Error in account handler: {str(e)}", exc_info=True)
        error_msg = get_message("error", language, error="Account info unavailable")
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=error_msg, parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            await update.effective_message.reply_text(
                text=error_msg, parse_mode=ParseMode.MARKDOWN_V2
            )


