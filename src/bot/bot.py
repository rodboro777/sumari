"""Main bot module that initializes and runs the Telegram bot."""

import asyncio
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    PreCheckoutQueryHandler,
    ContextTypes,
    Defaults,
)
from telegram.constants import ParseMode

from src.config import (
    TOKEN,
    logger,
    TON_CONFIG,
)
from src.services import VideoProcessor
from src.services import payment_processor
from src.services import AudioProcessor
from src.services import monitoring_service
from src.core.utils import (
    extract_video_id,
    get_user_language,
    get_user_preferences,
)
from src.core.localization import get_message
from src.core.keyboards import (
    create_main_menu_keyboard,
    create_menu_language_selection_keyboard,
)
from src.bot.handlers import (
    # Command handlers
    start,
    menu_command,
    help_command,
    about_command,
    set_language,
    button_callback,
    test_voice,
    test_tts,

    #Premium handlers
    premium_command,

    # Media handlers
    handle_audio_summary,
)

# Flask app for webhook
app = Flask(__name__)

# Create a single application instance
# Create bot instance
bot = Bot(TOKEN)

# Initialize the bot application
defaults = Defaults(parse_mode=ParseMode.MARKDOWN_V2)
application = ApplicationBuilder().token(TOKEN).defaults(defaults).build()

# Initialize payment processor with bot instance
payment_processor.bot = application.bot

# Error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error
    logger.error("Exception while handling an update:", exc_info=context.error)

    # Extract the error message
    if isinstance(context.error, Exception):
        error_msg = str(context.error)
    else:
        error_msg = "An unknown error occurred"

    # Log to monitoring service
    monitoring_service.log_error("telegram_bot", error_msg)

    # Send message to user if possible
    if update and isinstance(update, Update) and update.effective_chat:
        language = get_user_language(context, update.effective_user.id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=get_message("error_occurred", language),
            parse_mode=ParseMode.MARKDOWN_V2,
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages and URLs."""
    try:
        text = update.message.text
        user_id = update.effective_user.id
        language = get_user_language(context, user_id)

        # Check if it's a YouTube URL
        video_id = extract_video_id(text)
        if video_id:
            # Show processing message
            processing_msg = await update.message.reply_text(
                text=get_message("processing_summary", language),
                parse_mode=ParseMode.MARKDOWN_V2,
            )

            # Process YouTube video with both summarization methods
            video_processor = VideoProcessor()
            success, result = await video_processor.process_link(
                link=f"https://www.youtube.com/watch?v={video_id}",
                user_id=user_id,
                language=language,
                summary_type="both",
            )

            # Handle result
            if success:
                await video_processor.send_summary(
                    chat_id=update.effective_chat.id,
                    summary_data=result,
                    language=language,
                )
            else:
                logger.error(f"Failed to process video {video_id}: {result}")
                await update.message.reply_text(
                    text=get_message("error_processing", language),
                    parse_mode=ParseMode.MARKDOWN_V2,
                )

            # Delete processing message
            await processing_msg.delete()
        else:
            logger.info(f"Received non-URL text from user {user_id}: {text[:50]}...")
            await update.message.reply_text(
                text=get_message("not_youtube_url", language),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=create_main_menu_keyboard(language),
            )
    except Exception as e:
        logger.error(f"Error in handle_text: {str(e)}", exc_info=True)
        raise


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

    # Premium handlers
    application.add_handler(CommandHandler("premium", premium_command))

    # General handlers
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )
    application.add_handler(
        CallbackQueryHandler(handle_audio_summary, pattern="^get_audio_summary$")
    )
    application.add_error_handler(error_handler)


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
