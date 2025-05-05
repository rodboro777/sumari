"""Premium-related command handlers."""

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import logging

from src.core.keyboards.premium import create_support_menu_keyboard
from src.core.keyboards.payment import (
    create_payment_method_keyboard,
    create_payment_provider_keyboard,
)
from src.core.localization import get_message
from src.core.utils.formatting import format_expiry_date, format_premium_status
from src.database.db_manager import db_manager
from src.bot.utils import get_user_language
from src.services.payments import PaymentProcessor
from src.config import STRIPE_CONFIG

logger = logging.getLogger(__name__)


async def handle_premium(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle premium menu and related callbacks."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)

        premium_status = db_manager.get_premium_status(user_id) or {}
        tier = premium_status.get("tier", "free")
        is_pro = tier == "pro"
        is_based = tier == "based"
        is_free = tier == "free"

        # Format the message with user data
        formatted_message = format_premium_status(premium_status, language)

        # Create markup with appropriate upgrade buttons
        keyboard = []
        if is_free:
            keyboard.extend(
                [
                    [
                        InlineKeyboardButton(
                            get_message("btn_upgrade_based", language),
                            callback_data="subscribe_based",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            get_message("btn_upgrade_pro", language),
                            callback_data="subscribe_pro",
                        )
                    ],
                ]
            )
        elif is_based:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        get_message("btn_upgrade_pro", language),
                        callback_data="subscribe_pro",
                    )
                ]
            )

        # Add support and cancel buttons side by side if subscribed
        if not is_free:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        get_message("btn_cancel_subscription", language),
                        callback_data="cancel_subscription",
                    ),
                    InlineKeyboardButton(
                        get_message("btn_support", language),
                        callback_data="show_support_menu",
                    ),
                ]
            )
        else:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        get_message("btn_support", language),
                        callback_data="show_support_menu",
                    )
                ]
            )

        keyboard.append(
            [
                InlineKeyboardButton(
                    get_message("btn_back", language),
                    callback_data="back_to_menu",
                )
            ]
        )
        markup = InlineKeyboardMarkup(keyboard)

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
        error_text = get_message("error", language).format(error=str(e))
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=error_text, parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            await update.message.reply_text(
                text=error_text, parse_mode=ParseMode.MARKDOWN_V2
            )


async def handle_support_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle support menu."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)

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
        error_text = get_message("error", language, error=str(e))
        if update.callback_query:
            await update.callback_query.edit_message_text(
                error_text, parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            await update.message.reply_text(
                error_text, parse_mode=ParseMode.MARKDOWN_V2
            )


async def handle_payment_method(
    update: Update, context: ContextTypes.DEFAULT_TYPE, tier: str
) -> None:
    """Handle payment method selection."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)

        new_text = get_message("payment_method", language)
        new_markup = create_payment_method_keyboard(language, tier)

        await update.callback_query.edit_message_text(
            new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
        )

    except Exception as e:
        logger.error(f"Error in payment method handler: {e}", exc_info=True)
        error_text = (get_message("error", language)).format(error=str(e))
        await update.callback_query.edit_message_text(
            error_text, parse_mode=ParseMode.MARKDOWN_V2
        )


async def handle_payment_provider(
    update: Update, context: ContextTypes.DEFAULT_TYPE, method: str, tier: str
) -> None:
    """Handle payment provider selection."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)

        new_text = get_message("payment_provider", language)
        new_markup = create_payment_provider_keyboard(language, method, tier)

        await update.callback_query.edit_message_text(
            new_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_markup
        )

    except Exception as e:
        logger.error(f"Error in payment provider handler: {e}", exc_info=True)
        error_text = (get_message("error", language)).format(error=str(e))
        await update.callback_query.edit_message_text(
            error_text, parse_mode=ParseMode.MARKDOWN_V2
        )


async def handle_payment_creation(
    update: Update, context: ContextTypes.DEFAULT_TYPE, provider: str, tier: str
) -> None:
    """Handle payment creation."""
    try:
        query = update.callback_query
        await query.answer()

        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        language = get_user_language(context, user_id)

        # Initialize payment processor with Stripe
        payment_processor = PaymentProcessor(db_manager, STRIPE_CONFIG["secret_key"])

        if provider == "stripe":
            # Create Stripe checkout session
            success, result = await payment_processor.create_stripe_payment(
                tier=tier,
                user_id=user_id,
                chat_id=chat_id
            )

            if not success:
                await query.edit_message_text(
                    text=get_message("payment_error", language).format(error=result["error"]),
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
                return

            # Send checkout URL to user
            checkout_url = result["checkout_url"]
            message = get_message("stripe_checkout", language).format(url=checkout_url)
            keyboard = [
                [InlineKeyboardButton("🔗 Checkout", url=checkout_url)],
                [InlineKeyboardButton(
                    get_message("btn_back", language),
                    callback_data=f"payment_provider_{tier}"
                )]
            ]

            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN_V2
            )

        else:
            # Handle other payment providers
            await query.edit_message_text(
                text=get_message("payment_provider_unavailable", language),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=create_payment_provider_keyboard(language, tier)
            )

    except Exception as e:
        logger.error(f"Error in payment creation handler: {e}", exc_info=True)
        error_text = get_message("error", language).format(error=str(e))
        await query.edit_message_text(
            text=error_text,
            parse_mode=ParseMode.MARKDOWN_V2
        )


async def handle_cancel_subscription_confirm(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle subscription cancellation confirmation."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)

        premium_status = db_manager.get_premium_status(user_id) or {}
        expiry_date = premium_status.get("expiry_date")

        message = get_message("cancel_subscription_confirm", language).format(
            expiry=format_expiry_date(expiry_date, language)
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    get_message("btn_confirm_cancel", language),
                    callback_data="confirm_cancel_subscription",
                ),
                InlineKeyboardButton(
                    get_message("btn_keep_subscription", language),
                    callback_data="keep_subscription",
                ),
            ],
            [
                InlineKeyboardButton(
                    get_message("btn_back", language),
                    callback_data="back_to_premium",
                )
            ],
        ]
        markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            text=message,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=markup,
        )

    except Exception as e:
        logger.error(
            f"Error in cancel subscription confirm handler: {e}", exc_info=True
        )
        error_text = get_message("error", language).format(error=str(e))
        await update.callback_query.edit_message_text(
            text=error_text, parse_mode=ParseMode.MARKDOWN_V2
        )


async def handle_cancel_subscription(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle actual subscription cancellation."""
    try:
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)

        premium_status = db_manager.get_premium_status(user_id) or {}
        expiry_date = premium_status.get("expiry_date")

        # Cancel the subscription
        db_manager.cancel_subscription(user_id)

        message = get_message("subscription_cancelled", language).format(
            expiry=format_expiry_date(expiry_date, language)
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    get_message("btn_back", language),
                    callback_data="back_to_premium",
                )
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            text=message,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=markup,
        )

    except Exception as e:
        logger.error(f"Error in cancel subscription handler: {e}", exc_info=True)
        error_text = get_message("error", language).format(error=str(e))
        await update.callback_query.edit_message_text(
            text=error_text, parse_mode=ParseMode.MARKDOWN_V2
        )
