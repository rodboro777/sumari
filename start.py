"""Script to start the Telegram bot with Stripe webhook support."""

import asyncio
from src.main import main

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
