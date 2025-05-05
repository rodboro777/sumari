from fastapi import FastAPI, Request, HTTPException
import stripe
import os
import hmac
import hashlib
from src.services.payments import PaymentProcessor
from src.config import NOWPAYMENTS_CONFIG

app = FastAPI()

@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    # Get the raw request body
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        # Verify webhook signature
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )

        # Get payment processor instance
        payment_processor = PaymentProcessor()

        # Process the webhook event
        success, message = await payment_processor.handle_stripe_webhook(event)
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
            
        return {"status": "success", "message": message}

    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/nowpayments-webhook")
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
            NOWPAYMENTS_CONFIG["ipn_secret"].encode('utf-8'),
            payload,
            hashlib.sha512
        ).hexdigest()

        if not hmac.compare_digest(signature, auth_header):
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Parse the payload
        event_data = await request.json()

        # Get payment processor instance
        payment_processor = PaymentProcessor()

        # Process the webhook event
        success, message = await payment_processor.handle_nowpayments_webhook(event_data)
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
            
        return {"status": "success", "message": message}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
