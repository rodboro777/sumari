"""Module for handling upgrade prompts and notifications."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from src.core.localization import get_message
from src.core.utils import get_user_language
from src.config import TIER_LIMITS


async def send_upgrade_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, summaries_used: int) -> None:
    """Send an upgrade prompt when user is close to their limit."""
    user_id = update.effective_user.id
    language = get_user_language(context, user_id)
    
    # Get free tier limit
    free_limit = TIER_LIMITS["free"]["monthly_summaries"]
    remaining = free_limit - summaries_used
    
    # Create upgrade keyboard
    keyboard = [
        [
            InlineKeyboardButton("⭐️ Upgrade to Pro", callback_data="upgrade_pro"),
            InlineKeyboardButton("📊 View Plans", callback_data="view_plans")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Format message based on remaining summaries
    if remaining == 2:  # 3/5 used
        message = (
            "🌟 *Enjoying Sumari?*\n\n"
            "You've used 3 out of 5 free summaries this month\\. "
            "Upgrade to Pro for:\n"
            "• 200 summaries/month\n"
            "• Priority processing\n"
            "• Audio summaries\n"
            "• Premium support\n\n"
            "You have *2 summaries* remaining\\."
        )
    elif remaining == 1:  # 4/5 used
        message = (
            "⚡️ *Last Summary Approaching*\n\n"
            "You're about to use your last free summary this month\\. "
            "Don't let your productivity stop here\\!\n\n"
            "Upgrade to Pro now and get:\n"
            "• 200 summaries/month\n"
            "• Priority processing\n"
            "• Audio summaries\n"
            "• Premium support"
        )
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=reply_markup
    )
