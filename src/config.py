import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

# API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# GCP Configuration
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME", "sumari-audio-bucket")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
if not GCP_PROJECT_ID:
    logger.warning("GCP_PROJECT_ID not set. Audio storage features will be disabled.")

# Payment provider token (for Telegram Payments)
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN")
if not PAYMENT_PROVIDER_TOKEN:
    raise ValueError("PAYMENT_PROVIDER_TOKEN environment variable is not set")

# Supported languages
LANGUAGES = {
    "en": "English",
    "es": "Español",
    "pt": "Português",
    "hi": "हिंदी",
    "ru": "Русский",
    "ar": "العربية",
    "id": "Bahasa Indonesia",
    "fr": "Français",
    "de": "Deutsch",
    "tr": "Türkçe",
    "uk": "Українська",
}

# Summary languages (languages available for summary generation)
SUMMARY_LANGUAGES = {
    "en": "🇺🇸 English",
    "es": "🇪🇸 Spanish",
    "pt": "🇵🇹 Portuguese",
    "hi": "🇮🇳 Hindi",
    "ru": "🇷🇺 Russian",
    "ar": "🇸🇦 Arabic",
    "id": "🇮🇩 Indonesian",
    "fr": "🇫🇷 French",
    "de": "🇩🇪 German",
    "tr": "🇹🇷 Turkish",
    "uk": "🇺🇦 Ukrainian",
}

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="data/bot.log",
)
logger = logging.getLogger(__name__)

# Rate limiting
RATE_LIMIT_SECONDS = 60  # Time between allowed requests
MAX_REQUESTS_PER_MINUTE = 5

# Summary settings
MIN_TRANSCRIPT_LENGTH = 50  # Minimum length of transcript to generate summary
MAX_HISTORY_SIZE = 10  # Maximum number of summaries to keep in history

# Payment Provider Credentials
STRIPE_CONFIG = {
    "secret_key": os.getenv("STRIPE_SECRET_KEY"),
    "webhook_secret": os.getenv("STRIPE_WEBHOOK_SECRET"),
    "success_url": os.getenv("STRIPE_SUCCESS_URL", "https://your-domain.com/success"),
    "cancel_url": os.getenv("STRIPE_CANCEL_URL", "https://your-domain.com/cancel"),
}

TON_CONFIG = {
    "based_wallet": os.getenv("TON_BASED_WALLET"),
    "pro_wallet": os.getenv("TON_PRO_WALLET"),
}

# NOWPayments Configuration
NOWPAYMENTS_CONFIG = {
    "api_key": os.getenv("NOWPAYMENTS_API_KEY"),
    "ipn_secret": os.getenv("NOWPAYMENTS_IPN_SECRET"),
    "success_url": os.getenv("NOWPAYMENTS_SUCCESS_URL", "https://your-domain.com/success"),
    "cancel_url": os.getenv("NOWPAYMENTS_CANCEL_URL", "https://your-domain.com/cancel"),
}

# Create a .env file template if it doesn't exist
if not os.path.exists(".env"):
    with open(".env", "w") as f:
        f.write(
            """# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_SUCCESS_URL=https://your-domain.com/success
STRIPE_CANCEL_URL=https://your-domain.com/cancel

# TON Configuration
TON_BASED_WALLET=your_based_wallet_address
TON_PRO_WALLET=your_pro_wallet_address

# NOWPayments Configuration
NOWPAYMENTS_API_KEY=your_api_key
NOWPAYMENTS_IPN_SECRET=your_ipn_secret
NOWPAYMENTS_SUCCESS_URL=https://your-domain.com/success
NOWPAYMENTS_CANCEL_URL=https://your-domain.com/cancel

# GCP Configuration
GCP_PROJECT_ID=sumari-458514
GCP_BUCKET_NAME=sumari-audio-bucket

# Sesame AI Configuration
SESAME_API_KEY=your_sesame_api_key
"""
        )

# In src/config.py, add after GCP Configuration section:
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not GOOGLE_APPLICATION_CREDENTIALS:
    logger.warning("GOOGLE_APPLICATION_CREDENTIALS not set. Using default credentials.")
