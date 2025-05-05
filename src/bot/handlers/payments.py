"""Payment handlers module for managing premium subscriptions and payment processing."""

from telegram import Update, PreCheckoutQuery, LabeledPrice
from telegram.ext import ContextTypes
from telegram.error import TelegramError
import logging

from src.core.keyboards import (
    create_premium_options_keyboard,
    create_premium_status_keyboard,
    create_ton_payment_keyboard,
    create_payment_method_keyboard,
    create_payment_provider_keyboard,
    create_currency_keyboard,
)
from src.core.localization import get_message
from src.services.payments import PaymentProcessor
from src.database.db_manager import DatabaseManager
from src.config import PAYMENT_PROVIDER_TOKEN
from src.bot.utils import get_user_language

logger = logging.getLogger(__name__)


async def premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /premium command."""
    try:
        user_id = update.effective_user.id
        user_lang = get_user_language(context, user_id)
        db_manager = DatabaseManager()
        payment_processor = PaymentProcessor(db_manager, PAYMENT_PROVIDER_TOKEN)

        # Check current premium status
        premium_status = await payment_processor.check_premium_status(user_id)
        tier = premium_status.get("tier", "free")

        if tier == "free":
            # Show premium options using localized text
            message = get_message("premium_options", user_lang)
            keyboard = create_premium_options_keyboard(user_lang, is_subscribed=False)
        else:
            # Show current premium status for premium users
            message = get_message("premium_status_active", user_lang).format(
                tier=tier.upper(),
                activation_date=premium_status.get("activation_date", "N/A"),
                expiry_date=premium_status.get("expiry_date", "N/A"),
                renewal_date=premium_status.get(
                    "expiry_date", "N/A"
                ),  # Same as expiry for now
                summaries_used=premium_status.get("summaries_used", 0),
                summaries_limit=(
                    "∞"
                    if premium_status.get("summaries_limit", 0) == -1
                    else premium_status.get("summaries_limit", 0)
                ),
                audio_used=premium_status.get("audio_used", 0),
                processing_time=premium_status.get("total_processing_time", "0s"),
            )
            keyboard = create_premium_status_keyboard(user_lang)

        await update.message.reply_text(
            text=message, reply_markup=keyboard, parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in premium command: {str(e)}", exc_info=True)
        await update.message.reply_text(
            get_message("error", user_lang).format(str(e)), parse_mode="Markdown"
        )


async def handle_premium_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle callbacks from premium-related buttons."""
    try:
        query = update.callback_query
        await query.answer()

        user_id = update.effective_user.id
        user_lang = get_user_language(context, user_id)
        callback_data = query.data

        db_manager = DatabaseManager()
        payment_processor = PaymentProcessor(db_manager, PAYMENT_PROVIDER_TOKEN)

        if callback_data.startswith("premium_"):
            tier = callback_data.split("_")[1]  # 'based' or 'pro'

            if callback_data.endswith("_ton"):
                # Handle TON payment
                payment_data = await payment_processor.create_ton_payment(user_id, tier)
                message = get_message("ton_payment_details", user_lang).format(
                    amount=payment_data["amount"], wallet=payment_data["wallet"]
                )
                keyboard = create_ton_payment_keyboard(user_lang, tier)
            else:
                # Handle Telegram Payments
                title = f"Premium {tier.capitalize()} Subscription"
                description = get_message("premium_options", user_lang)
                payload = f"premium_{tier}"

                prices = [
                    LabeledPrice(label=title, amount=499 if tier == "based" else 999)
                ]

                await context.bot.send_invoice(
                    chat_id=user_id,
                    title=title,
                    description=description,
                    payload=payload,
                    provider_token=PAYMENT_PROVIDER_TOKEN,
                    currency="EUR",
                    prices=prices,
                )
                return

            await query.edit_message_text(
                text=message, reply_markup=keyboard, parse_mode="Markdown"
            )

        elif callback_data == "check_ton_payment":
            # Check TON payment status
            payment_status = await payment_processor.check_ton_payment_status(user_id)

            if payment_status["status"] == "completed":
                await payment_processor.process_successful_payment(
                    user_id, payment_status["amount"], payment_status["tier"]
                )
                message = get_message("payment_success", user_lang)
                keyboard = create_premium_status_keyboard(user_lang)
            elif payment_status["status"] == "pending":
                message = get_message("payment_pending", user_lang)
                keyboard = query.message.reply_markup
            else:
                message = get_message("payment_error", user_lang)
                keyboard = create_premium_options_keyboard(user_lang)

            await query.edit_message_text(
                text=message, reply_markup=keyboard, parse_mode="Markdown"
            )

    except Exception as e:
        await query.edit_message_text(
            get_message("error", user_lang).format(str(e)), parse_mode="Markdown"
        )


async def precheckout_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle pre-checkout queries."""
    query = update.pre_checkout_query
    try:
        await query.answer(ok=True)
    except TelegramError as e:
        logger.error(f"Error in pre-checkout: {e}")
        await query.answer(ok=False, error_message=str(e))


async def successful_payment_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle successful payments."""
    try:
        user_id = update.effective_user.id
        user_lang = get_user_language(context, user_id)
        payment = update.message.successful_payment
        tier = payment.invoice_payload.split("_")[1]

        db_manager = DatabaseManager()
        payment_processor = PaymentProcessor(db_manager, PAYMENT_PROVIDER_TOKEN)

        # Process the payment
        await payment_processor.process_successful_payment(
            user_id, payment.total_amount, tier
        )

        # Send confirmation message
        await update.message.reply_text(
            get_message("payment_success", user_lang), parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(
            get_message("payment_error", user_lang).format(str(e)),
            parse_mode="Markdown",
        )
