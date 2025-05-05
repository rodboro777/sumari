import asyncio
import uvicorn
from src.bot.bot import application, payment_processor
from src.routes import app as webhook_app

def main():
    # Add payment processor to FastAPI app state
    webhook_app.state.payment_processor = payment_processor
    
    # Run the bot with polling
    application.run_polling(
        allowed_updates=["message", "callback_query", "pre_checkout_query"],
        drop_pending_updates=True
    )

if __name__ == "__main__":
    print("Starting bot and webhook server...")
    asyncio.run(main())
