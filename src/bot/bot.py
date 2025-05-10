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
from src.core.utils import (
    extract_video_id,
    get_user_language,
    calculate_eta,
    format_eta,
    handle_error,
    are_notifications_enabled,
)
from src.core.utils.text import escape_md
from src.core.utils.security import security_check
from src.core.localization import get_message
from src.core.keyboards import create_main_menu_keyboard
from src.bot.handlers.basic import start
from src.bot.handlers.limits import check_summary_limits_and_notify
from src.bot.handlers import (
    menu_command,
    help_command,
    about_command,
    language_menu_command,
)
from src.bot.handlers import (
    # Premium handlers
    handle_premium,
    # Media handlers
    handle_audio_summary,
    # Command handlers
    button_callback,
)
from src.core.utils.error_handler import handle_error

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

# Configure error handler
application.add_error_handler(handle_error)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages and URLs."""
    try:
        text = update.message.text
        user_id = update.effective_user.id
        language = get_user_language(user_id)
        notifications_enabled = are_notifications_enabled(user_id)

        # Perform security checks first
        is_allowed, error_message = await security_check(update)
        if not is_allowed:
            if error_message == "not_youtube_url":
                await update.message.reply_text(
                    text=escape_md(get_message("not_youtube_url", language)),
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=create_main_menu_keyboard(language),
                    disable_notification=not notifications_enabled,
                )
            else:
                await update.message.reply_text(
                    text=escape_md(
                        get_message("security_error", language).format(
                            error=error_message
                        )
                    ),
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_notification=not notifications_enabled,
                )
            return

        # Extract video ID and process
        video_id = extract_video_id(text)
        if not video_id:
            # This should not happen as security check already validates URL
            logger.error(
                f"Failed to extract video ID after security check passed: {text[:50]}..."
            )
            await update.message.reply_text(
                text=escape_md(get_message("invalid_url", language)),
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_notification=not notifications_enabled,
            )
            return

        # First check if user has hit their limits
        can_proceed = await check_summary_limits_and_notify(update)
        if not can_proceed:
            return

        # Show initial processing message
        processing_msg = await update.message.reply_text(
            text=get_message("fetching", language),
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_notification=not notifications_enabled,
        )

        # Initialize video processor
        video_processor = VideoProcessor()

        try:
            # Try to extract content first
            content = await video_processor._extract_content(
                f"https://www.youtube.com/watch?v={video_id}"
            )
            if not content:
                raise ValueError("No transcript available")

            # Calculate ETA based on content length
            content_length = len(content)
            eta_seconds = calculate_eta(content_length)
            eta_text = format_eta(eta_seconds)

            # Update message with ETA
            await processing_msg.edit_text(
                text=get_message("processing_video", language).format(eta=eta_text),
                parse_mode=ParseMode.MARKDOWN_V2,
            )

            # Show summarizing message
            await processing_msg.edit_text(
                text=get_message("summarizing", language),
                parse_mode=ParseMode.MARKDOWN_V2,
            )

            # Process YouTube video with Gemini only
            success, result = await video_processor.process_link(
                link=f"https://www.youtube.com/watch?v={video_id}",
                user_id=user_id,
                language=language,
                summary_type="gemini",
            )

            # Handle result
            if success:
                await video_processor.send_summary(
                    bot=context.bot,
                    chat_id=update.effective_chat.id,
                    summary_data=result,
                    language=language,
                    disable_notification=not notifications_enabled,
                )
            else:
                logger.error(f"Failed to process video {video_id}: {result}")
                await update.message.reply_text(
                    text=escape_md(
                        get_message("error_processing", language).format(
                            error=result["error"]
                        )
                    ),
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_notification=not notifications_enabled,
                )
        except Exception as e:
            logger.error(f"Error processing video {video_id}: {str(e)}")
            await update.message.reply_text(
                text=escape_md(
                    get_message("error_processing", language).format(error=str(e))
                ),
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_notification=not notifications_enabled,
            )
        finally:
            # Always try to delete the processing message
            try:
                await processing_msg.delete()
            except Exception as e:
                logger.error(f"Error deleting processing message: {str(e)}")

    except Exception as e:
        logger.error(f"Error in handle_text: {str(e)}", exc_info=True)
        error_text = escape_md(get_message("error", language).format(error=str(e)))
        await update.message.reply_text(
            text=error_text,
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_notification=not notifications_enabled,
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
    application.add_handler(CommandHandler("language", language_menu_command))
    application.add_handler(CommandHandler("premium", handle_premium))

    # General handlers
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )
    application.add_handler(
        CallbackQueryHandler(handle_audio_summary, pattern="^get_audio_summary$")
    )
    application.add_error_handler(handle_error)


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
