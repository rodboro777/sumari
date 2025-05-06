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

webhook_app = FastAPI()
security = HTTPBasic()

# Add metrics middleware
webhook_app.middleware("http")(track_cloud_run_metrics_middleware)


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
    """Handle Telegram webhook updates."""
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return Response(content="OK", status_code=200)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@webhook_app.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    # Get the raw request body
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        # Verify webhook signature
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)

        # Process the webhook event
        success, message = await payment_processor.handle_stripe_webhook(event)

        if not success:
            raise HTTPException(status_code=400, detail=message)

        return {"status": "success", "message": message}

    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@webhook_app.post("/nowpayments-webhook")
async def nowpayments_webhook(request: Request):
    # Get the raw request body
    payload = await request.body()
    auth_header = request.headers.get("X-NOWPayments-Sig")

    try:
        # Verify webhook signature
        if not auth_header:
            raise HTTPException(status_code=400, detail="Missing signature header")

        # Calculate HMAC signature
        signature = hmac.new(
            NOWPAYMENTS_CONFIG["ipn_secret"].encode("utf-8"), payload, hashlib.sha512
        ).hexdigest()

        if not hmac.compare_digest(signature, auth_header):
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
        raise HTTPException(status_code=400, detail=str(e))


# Health check endpoint
@webhook_app.get("/")
def health_check():
    return {"status": "ok"}
