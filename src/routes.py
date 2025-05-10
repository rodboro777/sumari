from fastapi import FastAPI, Request, HTTPException, Depends, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import stripe
import os
import hmac
import hashlib
from src.services import payment_processor
from src.config import NOWPAYMENTS_CONFIG, TOKEN
from src.logging import metrics_router
from src.logging.api import track_cloud_run_metrics_middleware
from src.bot.bot import application
from telegram import Update
from src.core.utils.security import security_check

webhook_app = FastAPI()
security = HTTPBasic()

# Add rate limiting middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

webhook_app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # Configure this based on your deployment environment
)

# Add metrics middleware
webhook_app.middleware("http")(track_cloud_run_metrics_middleware)

# Rate limiting storage
from datetime import datetime, timedelta
from collections import defaultdict

webhook_requests = defaultdict(list)
WEBHOOK_RATE_LIMIT = 100  # requests per minute
WEBHOOK_WINDOW = 60  # seconds


def check_webhook_rate_limit(ip: str) -> bool:
    current_time = datetime.now()
    webhook_requests[ip] = [
        req_time
        for req_time in webhook_requests[ip]
        if current_time - req_time < timedelta(seconds=WEBHOOK_WINDOW)
    ]
    if len(webhook_requests[ip]) >= WEBHOOK_RATE_LIMIT:
        return False
    webhook_requests[ip].append(current_time)
    return True


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.getenv("ADMIN_USERNAME", "admin")
    correct_password = os.getenv("ADMIN_PASSWORD")

    if not correct_password:
        raise HTTPException(status_code=500, detail="Admin password not configured")

    if not (
        credentials.username == correct_username
        and credentials.password == correct_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


# Include metrics router with admin authentication
webhook_app.include_router(metrics_router, dependencies=[Depends(verify_admin)])


@webhook_app.post(f"/telegram-webhook/{TOKEN}")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook updates with security checks."""
    try:
        # Rate limiting check
        client_ip = request.client.host
        if not check_webhook_rate_limit(client_ip):
            raise HTTPException(status_code=429, detail="Too many requests")

        # Verify Telegram IP (optional but recommended)
        telegram_ips = [
            "149.154.160.0/20",
            "91.108.4.0/22",
        ]
        if not any(client_ip.startswith(ip.split("/")[0]) for ip in telegram_ips):
            logger.warning(f"Request from non-Telegram IP: {client_ip}")
            raise HTTPException(status_code=403, detail="Forbidden")

        data = await request.json()
        update = Update.de_json(data, application.bot)

        # Perform security checks on the update
        is_allowed, error_message = await security_check(update)
        if not is_allowed:
            logger.warning(f"Security check failed: {error_message}")
            raise HTTPException(status_code=400, detail=error_message)

        await application.process_update(update)
        return Response(content="OK", status_code=200)
    except Exception as e:
        logger.error(f"Error in telegram webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@webhook_app.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook with enhanced security."""
    try:
        # Rate limiting check
        client_ip = request.client.host
        if not check_webhook_rate_limit(client_ip):
            raise HTTPException(status_code=429, detail="Too many requests")

        # Get the raw request body
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")

        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing signature header")

        # Verify webhook signature
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        if not webhook_secret:
            raise HTTPException(status_code=500, detail="Webhook secret not configured")

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except stripe.error.SignatureVerificationError:
            logger.warning(f"Invalid Stripe signature from IP: {client_ip}")
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Process the webhook event
        success, message = await payment_processor.handle_stripe_webhook(event)
        if not success:
            raise HTTPException(status_code=400, detail=message)

        return {"status": "success", "message": message}

    except Exception as e:
        logger.error(f"Error in stripe webhook: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@webhook_app.post("/nowpayments-webhook")
async def nowpayments_webhook(request: Request):
    """Handle NOWPayments webhook with enhanced security."""
    try:
        # Rate limiting check
        client_ip = request.client.host
        if not check_webhook_rate_limit(client_ip):
            raise HTTPException(status_code=429, detail="Too many requests")

        # Get the raw request body
        payload = await request.body()
        auth_header = request.headers.get("X-NOWPayments-Sig")

        if not auth_header:
            raise HTTPException(status_code=400, detail="Missing signature header")

        # Calculate HMAC signature
        if not NOWPAYMENTS_CONFIG.get("ipn_secret"):
            raise HTTPException(status_code=500, detail="IPN secret not configured")

        # Calculate HMAC signature
        signature = hmac.new(
            NOWPAYMENTS_CONFIG["ipn_secret"].encode("utf-8"), payload, hashlib.sha512
        ).hexdigest()

        if not hmac.compare_digest(signature, auth_header):
            logger.warning(f"Invalid NOWPayments signature from IP: {client_ip}")
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Parse the payload
        event_data = await request.json()

        # Process the webhook event
        success, message = await payment_processor.handle_nowpayments_webhook(
            event_data
        )
        if not success:
            raise HTTPException(status_code=400, detail=message)

        return {"status": "success", "message": message}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"Error in nowpayments webhook: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Health check endpoint
@webhook_app.get("/")
def health_check():
    return {"status": "ok"}
