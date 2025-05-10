"""Premium-related command handlers."""

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import logging

from src.core.keyboards.payment import create_payment_method_keyboard
from src.core.keyboards.premium import (
    create_premium_options_keyboard,
    create_subscription_cancel_keyboard,
    create_subscription_cancelled_keyboard,
    create_support_menu_keyboard,
)
from src.core.localization import get_message
from src.core.utils import get_user_language, cancel_subscription, get_premium_status
from src.core.utils.text import escape_md
from src.services import payment_processor
from src.core.utils.formatting import format_expiry_date, format_premium_status

logger = logging.getLogger(__name__)


# DO NOT REMOVE CONTEXT FROM MENU COMMANDS,
# ITS PASSED BY TELEGRAM HANDLERS, EVEN THOUGH ITS NOT USED
async def handle_premium(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle premium menu and related callbacks."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(user_id)
        premium_status = get_premium_status(user_id) or {}
        tier = premium_status.get("tier", "free")
        is_pro = tier == "pro"
        is_based = tier == "based"
        is_free = tier == "free"

        # Format the message with user data
        formatted_message = format_premium_status(premium_status, language)

        # Create markup using premium keyboard functions
        markup = create_premium_options_keyboard(
            language=language,
            is_subscribed=not is_free,
            is_based=is_based,
            is_pro=is_pro,
            expired=False
        )

        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=formatted_message,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=markup,
            )
        else:
            await update.message.reply_text(
                text=formatted_message,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=markup,
            )

    except Exception as e:
        logger.error(f"Error in premium handler: {e}", exc_info=True)


async def handle_support_menu(update: Update) -> None:
    """Handle support menu."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(user_id)

        new_text = get_message("support_menu", language)
        new_markup = create_support_menu_keyboard(language)

        if update.callback_query:
            await update.callback_query.edit_message_text(
                new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
            )
        else:
            await update.message.reply_text(
                new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
            )

    except Exception as e:
        logger.error(f"Error in support menu handler: {e}", exc_info=True)


async def handle_payment_creation(update: Update, provider: str, tier: str) -> None:
    """Handle payment creation."""
    try:
        query = update.callback_query
        await query.answer()

        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        language = get_user_language(user_id)

        if provider == "stripe":
            # Create Stripe checkout session
            success, result = await payment_processor.create_stripe_payment(
                tier=tier, user_id=user_id, chat_id=chat_id
            )

            if not success:
                await query.edit_message_text(
                    text=escape_md(get_message("payment_error", language).format(
                        error=result["error"]
                    )),
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
                return

            # Send checkout URL to user
            checkout_url = result["checkout_url"]
            # Escape URL to prevent Markdown formatting issues
            escaped_url = escape_md(checkout_url)
            message = get_message("stripe_checkout", language).format(url=escaped_url)
            keyboard = [
                [InlineKeyboardButton("🔗 Checkout", url=checkout_url)],
                [
                    InlineKeyboardButton(
                        get_message("btn_back", language),
                        callback_data=f"premium_{tier}",
                    )
                ],
            ]

            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN_V2,
            )

        elif provider == "nowpayments":
            # Create NOWPayments payment
            success, result = await payment_processor.create_payment(
                tier=tier,
                user_id=user_id,
                chat_id=chat_id,
                provider="nowpayments",
                currency="USD",  # Default to USD, can be changed later
            )

            if not success:
                await query.edit_message_text(
                    text=escape_md(get_message("payment_error", language).format(
                        error=result["error"]
                    )),
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
                return

            # Send payment details to user
            payment_url = result.get("invoice_url")
            # Escape payment URL to prevent Markdown formatting issues
            escaped_url = escape_md(payment_url)
            message = get_message("nowpayments_checkout", language).format(
                url=escaped_url
            )
            keyboard = [
                [InlineKeyboardButton("🔗 Pay with Crypto", url=payment_url)],
                [
                    InlineKeyboardButton(
                        get_message("btn_back", language),
                        callback_data=f"premium_{tier}",
                    )
                ],
            ]

            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN_V2,
            )

        else:
            # Handle unsupported payment provider
            await query.edit_message_text(
                text=get_message("payment_provider_unavailable", language),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=create_payment_method_keyboard(language, tier),
            )

    except Exception as e:
        logger.error(f"Error in payment creation handler: {e}", exc_info=True)


async def handle_cancel_subscription_confirm(update: Update) -> None:
    """Handle subscription cancellation confirmation."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(user_id)
        expiry_date = get_premium_status(user_id).get("expiry_date")

        message = get_message("cancel_subscription_confirm", language).format(
            expiry=format_expiry_date(expiry_date, language)
        )

        markup = create_subscription_cancel_keyboard(language)

        await update.callback_query.edit_message_text(
            text=message,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=markup,
        )

    except Exception as e:
        logger.error(f"Error in cancel subscription confirm handler: {e}", exc_info=True)

async def handle_payment_method_selection(update: Update, tier: str) -> None:
    """Handle payment method selection."""
    query = update.callback_query
    user_id = update.effective_user.id
    language = get_user_language(user_id)

    await query.edit_message_text(
        text=get_message("payment_method", language),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=create_payment_method_keyboard(language, tier),
    )

async def handle_cancel_subscription(update: Update) -> None:
    """Handle actual subscription cancellation."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(user_id)
        expiry_date = get_premium_status(user_id).get("expiry_date")

        # Cancel the subscription
        cancel_subscription(user_id)

        message = get_message("subscription_cancelled", language).format(
            expiry=format_expiry_date(expiry_date, language)
        )

        markup = create_subscription_cancelled_keyboard(language)

        await update.callback_query.edit_message_text(
            text=message,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=markup,
        )

    except Exception as e:
        logger.error(f"Error in cancel subscription handler: {e}", exc_info=True)



