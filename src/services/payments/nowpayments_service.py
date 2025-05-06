"""NOWPayments API service."""

import aiohttp
import logging
from typing import Dict, Optional, Tuple
from src.config import NOWPAYMENTS_CONFIG

logger = logging.getLogger(__name__)


class NOWPaymentsService:
    """Service for handling NOWPayments API interactions."""

    def __init__(self):
        self.base_url = "https://api.nowpayments.io/v1"
        self.headers = {
            "Authorization": f"Bearer {NOWPAYMENTS_CONFIG['api_key']}",
            "Content-Type": "application/json",
        }

    async def create_payment(
        self,
        price_amount: float,
        price_currency: str = "USD",
        pay_currency: Optional[str] = None,
        order_id: Optional[str] = None,
        user_id: Optional[int] = None,
        **kwargs,
    ) -> Tuple[bool, Dict]:
        """Create a new crypto payment."""
        try:
            endpoint = f"{self.base_url}/payment"
            payload = {
                "price_amount": price_amount,
                "price_currency": price_currency,
                "order_id": order_id or "",
                "order_description": f"Premium subscription for user {user_id}",
                "ipn_callback_url": kwargs.get("callback_url", ""),
                "success_url": kwargs.get("success_url", ""),
                "cancel_url": kwargs.get("cancel_url", ""),
            }

            if pay_currency:
                payload["pay_currency"] = pay_currency

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint, json=payload, headers=self.headers
                ) as response:
                    if response.status == 201:
                        data = await response.json()
                        return True, data
                    else:
                        error_data = await response.text()
                        logger.error(f"NOWPayments API error: {error_data}")
                        return False, {"error": "Failed to create payment"}

        except Exception as e:
            logger.error(f"Error creating NOWPayments payment: {str(e)}")
            return False, {"error": str(e)}

    async def get_payment_status(self, payment_id: str) -> Tuple[bool, Dict]:
        """Get the status of a payment."""
        try:
            endpoint = f"{self.base_url}/payment/{payment_id}"

            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return True, data
                    else:
                        error_data = await response.text()
                        logger.error(f"NOWPayments API error: {error_data}")
                        return False, {"error": "Failed to get payment status"}

        except Exception as e:
            logger.error(f"Error getting NOWPayments payment status: {str(e)}")
            return False, {"error": str(e)}

    async def cancel_subscription(
        self, subscription_id: str, cancel_at_period_end: bool = True
    ) -> Tuple[bool, Dict]:
        """Cancel a NOWPayments subscription.

        Args:
            subscription_id: The ID of the subscription to cancel
            cancel_at_period_end: If True, subscription will remain active until the end of the period
                                If False, subscription will be cancelled immediately

        Returns:
            Tuple[bool, Dict]: Success status and result/error message
        """
        try:
            endpoint = f"{self.base_url}/subscription/{subscription_id}/cancel"
            payload = {"cancel_at_period_end": cancel_at_period_end}

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint, json=payload, headers=self.headers
                ) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        return True, data
                    else:
                        error_data = await response.text()
                        logger.error(f"NOWPayments API error: {error_data}")
                        return False, {"error": "Failed to cancel subscription"}

        except Exception as e:
            logger.error(f"Error cancelling NOWPayments subscription: {str(e)}")
            return False, {"error": str(e)}
