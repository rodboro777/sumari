import asyncio
import uvicorn
from src.bot.bot import application, payment_processor
from src.routes import webhook_app
from telegram import Bot
from src.config import TOKEN
import os
import threading
from contextlib import asynccontextmanager


async def setup_webhook(url):
    """Set up webhook for the bot."""
    bot = Bot(TOKEN)
    # Remove any existing webhooks first
    await bot.delete_webhook()
    # Set up new webhook
    await bot.set_webhook(f"{url}/telegram-webhook/{TOKEN}")
    print(f"Webhook set up at {url}/telegram-webhook/{TOKEN}")


def run_fastapi():
    """Run the FastAPI server in a separate thread."""
    uvicorn.run(webhook_app, host="0.0.0.0", port=8000, log_level="info", reload=False)


@asynccontextmanager
async def bot_runtime():
    """Context manager for bot lifecycle."""
    try:
        await application.initialize()
        await application.start()
        yield
    finally:
        await application.stop()


async def run_bot():
    print("Bot application started successfully")
    await application.run_polling(drop_pending_updates=True, close_loop=False)

async def main():
    # Add payment processor to FastAPI app state
    webhook_app.state.payment_processor = payment_processor

    # Get the public URL from environment variable (set by ngrok)
    public_url = os.getenv("PUBLIC_URL")
    if not public_url:
        print("Please set PUBLIC_URL environment variable with your ngrok URL")
        return

    # Setup webhook
    await setup_webhook(public_url)

    # Start FastAPI in a separate thread
    fastapi_thread = threading.Thread(target=run_fastapi)
    fastapi_thread.daemon = True
    fastapi_thread.start()

    # Start the bot
    print("Starting bot application...")
    await run_bot()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
