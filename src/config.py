import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
# Create logs directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Configure file handler
file_handler = logging.FileHandler("data/bot.log")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(file_formatter)

# Configure console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# Get logger for this module
logger = logging.getLogger(__name__)

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

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not GOOGLE_APPLICATION_CREDENTIALS:
    logger.warning("GOOGLE_APPLICATION_CREDENTIALS not set. Using default credentials.")

# Payment provider token (for Telegram Payments)
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN")
if not PAYMENT_PROVIDER_TOKEN:
    raise ValueError("PAYMENT_PROVIDER_TOKEN environment variable is not set")

# Summary Length Configuration
MAX_SUMMARY_LENGTH = {
    "short": 1500,  # ~1.5k characters
    "medium": 3000,  # ~3k characters
    "long": 5000,  # ~5k characters
}

# Tier and Usage Limits
TIER_LIMITS = {
    "free": {
        "summaries_per_month": 5,  # 5 summaries per month
        "max_users": 2000,  # Cap at 2000 free users
        "fallback_max_users": 1200,  # Fallback cap if conversion rate is low
    },
    "based": {
        "summaries_per_month": 100,  # 100 summaries per month
        "max_users": 500,  # No strict cap, but monitor
    },
    "pro": {
        "summaries_per_month": 200,  # 200 summaries per month
        "max_users": 100,  # Cap at 100 pro users
    },
}

# Conversion Thresholds
MIN_PAID_USERS_RATIO = 0.05  # 5% of free users should convert to paid

# Rate limiting (per request)
RATE_LIMIT_SECONDS = 560  # Time between allowed requests
MAX_REQUESTS_PER_MINUTE = 5

# Payment Provider Credentials
STRIPE_CONFIG = {
    "secret_key": os.getenv("STRIPE_SECRET_KEY"),
    "webhook_secret": os.getenv("STRIPE_WEBHOOK_SECRET"),
    "success_url": os.getenv(
        "STRIPE_SUCCESS_URL", "https://sumari-e218a.web.app/payment/success"
    ),
    "cancel_url": os.getenv(
        "STRIPE_CANCEL_URL", "https://sumari-e218a.web.app/payment/fail"
    ),
    "tiers": {
        "based": {
            "name": "based",
            "description": "100 summaries per month",
            "summaries_limit": 100,
            "duration_days": 30,
            "features": ["100 summaries/month", "Text summaries"],
            "stripe_product_id": "prod_SFe1nUFkkKHG5j",
        },
        "pro": {
            "name": "pro",
            "description": "Unlimited summaries + Audio versions",
            "summaries_limit": 200,
            "duration_days": 30,
            "features": [
                "200 summaries/month",
                "Text & Audio summaries",
                "Priority processing",
            ],
            "stripe_product_id": "prod_SFe2WqvSrS2sA7",
        },
    },
}

TON_CONFIG = {
    "based_wallet": os.getenv("TON_BASED_WALLET"),
    "pro_wallet": os.getenv("TON_PRO_WALLET"),
}

# NOWPayments Configuration
NOWPAYMENTS_CONFIG = {
    "api_key": os.getenv("NOWPAYMENTS_API_KEY"),
    "ipn_secret": os.getenv("NOWPAYMENTS_IPN_SECRET"),
    "success_url": os.getenv(
        "NOWPAYMENTS_SUCCESS_URL", "https://your-domain.com/success"
    ),
    "cancel_url": os.getenv("NOWPAYMENTS_CANCEL_URL", "https://your-domain.com/cancel"),
}
