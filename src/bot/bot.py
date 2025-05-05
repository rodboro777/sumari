"""Main bot module that initializes and runs the Telegram bot."""

import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    PreCheckoutQueryHandler,
)
from telegram.constants import ParseMode

from src.config import (
    TOKEN,
    logger,
    GEMINI_API_KEY,
    STRIPE_CONFIG,
    TON_CONFIG,
)
from src.database.db_manager import db_manager
from src.services.video_processor import VideoProcessor
from src.services.monitoring import MonitoringService
from src.services.payments import PaymentProcessor
from src.services.audio_processor import AudioProcessor
from src.core.utils import extract_video_id
from src.core.localization import get_message
from src.core.keyboards import create_main_menu_keyboard
from src.bot.utils import get_user_language, get_user_preferences
from src.bot.handlers.basic import (
    start,
    menu_command,
    help_command,
    about_command,
    set_language,
    button_callback,
    test_voice,
    test_tts,
)
from src.bot.handlers.payments import (
    premium_command,
    handle_premium_callback,
    precheckout_callback,
    successful_payment_callback,
)
from src.bot.handlers.modules import (
    handle_premium,
    handle_payment_method,
    handle_payment_provider,
    handle_payment_creation,
    handle_support_menu,
    handle_cancel_subscription_confirm,
    handle_cancel_subscription,
)

# Initialize services
monitoring_service = MonitoringService(db_manager)
video_processor = VideoProcessor(
    db_manager=db_manager,
    monitoring=monitoring_service,
    gemini_api_key=GEMINI_API_KEY,
)
audio_processor = AudioProcessor(
    db_manager=db_manager,
    monitoring=monitoring_service,
)
payment_processor = PaymentProcessor(
    db_manager=db_manager,
    stripe_secret_key=STRIPE_CONFIG["secret_key"],
)

# Update TON wallet addresses
payment_processor.ton_wallets = {
    "based": TON_CONFIG["based_wallet"],
    "pro": TON_CONFIG["pro_wallet"],
}

# Flask app for webhook
app = Flask(__name__)

# Create a single application instance
application = ApplicationBuilder().token(TOKEN).build()


async def handle_message(update: Update, context):
    """Handle incoming messages."""
    try:
        user_id = update.effective_user.id
        text = update.message.text
        language = get_user_language(context, user_id)

        # Check if the message is a YouTube URL
        video_id = extract_video_id(text)

        if video_id:
            # Process YouTube video
            await video_processor.process_video(
                video_id, user_id, get_user_preferences(context, user_id)
            )
        else:
            # Send help message for invalid input
            await update.message.reply_text(
                get_message("invalid_url", language),
                reply_markup=create_main_menu_keyboard(language),
                parse_mode=ParseMode.MARKDOWN_V2,
            )

    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await update.message.reply_text(
            get_message("error", language, error=str(e)),
            parse_mode=ParseMode.MARKDOWN_V2,
        )


# === OPTION 1: Webhook Approach ===
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Handle incoming webhook updates."""
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return "ok"


@app.route("/", methods=["GET"])
def index():
    """Health check endpoint."""
    return "Bot is online."


def add_handlers(application):
    """Add all handlers to the application."""
    # Basic command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("language", set_language))
    application.add_handler(CommandHandler("test_voice", test_voice))
    application.add_handler(CommandHandler("test_tts", test_tts))

    # Payment handlers
    application.add_handler(CommandHandler("premium", premium_command))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback)
    )
    application.add_handler(
        CallbackQueryHandler(handle_premium_callback, pattern="^(premium_stripe_|ton_)")
    )

    # General handlers
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # Store services in bot_data for access in handlers
    application.bot_data["video_processor"] = video_processor
    application.bot_data["audio_processor"] = audio_processor
    application.bot_data["payment_processor"] = payment_processor
    application.bot_data["monitoring"] = monitoring_service


# Initialize handlers
add_handlers(application)


# === OPTION 2: Polling Approach ===
def run_polling():
    """Run the bot using polling (for development)."""
    application.run_polling()


if __name__ == "__main__":
    # Choose ONE of these:
    # app.run()  # For production with a public server
    run_polling()  # For testing/development
