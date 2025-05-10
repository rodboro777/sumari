"""Optimized startup process for the application."""

import asyncio
import threading
from functools import lru_cache
import uvicorn
from contextlib import asynccontextmanager
from telegram import Bot
import firebase_admin
from firebase_admin import credentials
import logging

from src.config import TOKEN, logger
from src.bot.bot import application, payment_processor
from src.routes import webhook_app

# Configure startup logger
startup_logger = logging.getLogger("startup")


@lru_cache()
def initialize_firebase():
    """Lazy initialization of Firebase Admin SDK."""
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(
                "sumari-e218a-firebase-adminsdk-fbsvc-4237ee8346.json"
            )
            firebase_admin.initialize_app(cred)
            startup_logger.info("Firebase initialized successfully")
    except Exception as e:
        startup_logger.error(f"Firebase initialization error: {e}")
        raise


async def setup_webhook(url: str):
    """Set up webhook for the bot with error handling."""
    try:
        bot = Bot(TOKEN)
        await bot.delete_webhook()
        webhook_url = f"{url}/telegram-webhook/{TOKEN}"
        await bot.set_webhook(webhook_url)
        startup_logger.info(f"Webhook set up at {webhook_url}")
    except Exception as e:
        startup_logger.error(f"Webhook setup error: {e}")
        raise


def run_fastapi():
    """Run the FastAPI server in a separate thread with optimized settings."""
    try:
        uvicorn.run(
            webhook_app,
            host="0.0.0.0",
            port=8000,
            log_level="warning",  # Reduce logging
            reload=False,
            access_log=False,  # Disable access logs
            limit_concurrency=100,  # Limit concurrent connections
            timeout_keep_alive=30,  # Reduce keep-alive timeout
        )
    except Exception as e:
        startup_logger.error(f"FastAPI startup error: {e}")
        raise


@asynccontextmanager
async def bot_runtime():
    """Managed bot lifecycle."""
    try:
        await application.initialize()
        await application.start()
        startup_logger.info("Bot runtime initialized")
        yield
    finally:
        await application.stop()


async def run_bot():
    """Run the bot with optimized settings."""
    try:
        startup_logger.info("Starting bot application...")
        await application.run_polling(
            drop_pending_updates=True,
            close_loop=False,
            allowed_updates=[
                "message",
                "callback_query",
            ],  # Only listen for needed updates
            read_timeout=30,
            write_timeout=30,
        )
    except Exception as e:
        startup_logger.error(f"Bot runtime error: {e}")
        raise


async def initialize_services():
    """Initialize all services in parallel."""
    try:
        # Initialize Firebase in a thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, initialize_firebase)

        # Add payment processor to FastAPI state
        webhook_app.state.payment_processor = payment_processor

        startup_logger.info("All services initialized")
    except Exception as e:
        startup_logger.error(f"Service initialization error: {e}")
        raise


async def main():
    """Optimized main startup sequence."""
    try:
        startup_logger.info("Starting application...")

        # Initialize services first
        await initialize_services()

        # Start FastAPI in background
        fastapi_thread = threading.Thread(target=run_fastapi)
        fastapi_thread.daemon = True
        fastapi_thread.start()

        # Start the bot
        await run_bot()

    except Exception as e:
        startup_logger.error(f"Startup error: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        startup_logger.info("Application stopped by user")
    except Exception as e:
        startup_logger.error(f"Application error: {e}")
