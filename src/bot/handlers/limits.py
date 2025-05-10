from telegram import Update
from telegram.constants import ParseMode
from src.core.keyboards import create_premium_upgrade_keyboard
from src.core.localization import get_message
from src.core.utils import get_user_language
from src.core.utils import check_summary_limits


async def check_summary_limits_and_notify(update: Update) -> bool:
    """Check if user has hit summary limits and send appropriate notifications.

    Returns:
        bool: True if user can proceed with summary, False if limit reached
    """
    user_id = update.effective_user.id
    language = get_user_language(user_id)

    # Get limit info
    limit_info = check_summary_limits(user_id)

    if limit_info["has_reached_limit"]:
        # User has reached their limit
        await update.message.reply_text(
            text=get_message("summary_limit_reached", language).format(
                limit=limit_info["total_limit"]
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=create_premium_upgrade_keyboard(language),
        )
        return False

    remaining = limit_info["remaining_summaries"]
    tier = limit_info["tier"]
    used = limit_info["summaries_used"]
    total = limit_info["total_limit"]

    # Show warning when less than 30% remaining
    warning_threshold = total * 0.3

    if remaining <= warning_threshold:
        if tier == "free":
            await update.message.reply_text(
                text=get_message("summary_limit_warning_free", language).format(
                    remaining=remaining
                ),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=create_premium_upgrade_keyboard(language),
            )
        else:
            # For paid tiers (based/pro)
            await update.message.reply_text(
                text=get_message("summary_limit_warning_paid", language).format(
                    remaining=remaining, tier=tier
                ),
                parse_mode=ParseMode.MARKDOWN_V2,
            )

    # Show usage stats when less than 50% remaining
    if remaining <= total * 0.5:
        if tier == "free":
            await update.message.reply_text(
                text=get_message("summary_limit_near_free", language).format(
                    used=used, limit=total
                ),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=create_premium_upgrade_keyboard(language),
            )
        else:
            await update.message.reply_text(
                text=get_message("summary_limit_near_paid", language).format(
                    used=used, limit=total
                ),
                parse_mode=ParseMode.MARKDOWN_V2,
            )

    return True
