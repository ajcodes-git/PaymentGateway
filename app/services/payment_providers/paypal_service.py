import requests
from decimal import Decimal
from typing import Optional
from app.services.payment_providers.payment_interface import PaymentService
from app.utils.config import settings

class PayPalService(PaymentService):
    def __init__(self, sandbox: bool = True):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self.sandbox = sandbox
        self.base_url = "https://api.sandbox.paypal.com" if sandbox else "https://api.paypal.com"
        self.access_token = self._get_access_token()

    def _get_access_token(self) -> str:
        url = f"{self.base_url}/v1/oauth2/token"
        headers = {"Accept": "application/json", "Accept-Language": "en_US"}
        data = {"grant_type": "client_credentials"}
        res = requests.post(url, headers=headers, data=data, auth=(self.client_id, self.client_secret))
        res.raise_for_status()
        return res.json()["access_token"]

    def initiate_payment(self, amount: Decimal, currency: str, customer: dict, metadata: Optional[dict] = None) -> dict:
        url = f"{self.base_url}/v1/payments/payment"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }
        payload = {
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "transactions": [
                {
                    "amount": {
                        "total": f"{amount:.2f}",
                        "currency": currency,
                    },
                    "description": metadata.get("description") if metadata else "Payment",
                }
            ],
            "redirect_urls": {
                "return_url": metadata.get("return_url") if metadata else "http://example.com/return",
                "cancel_url": metadata.get("cancel_url") if metadata else "http://example.com/cancel",
            },
        }
        res = requests.post(url, headers=headers, json=payload)
        res.raise_for_status()

        return {"res": res.json(), "gateway_ref": res.json()["id"]}

    def verify_payment(self, transaction_id: str) -> dict:
        url = f"{self.base_url}/v1/payments/payment/{transaction_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        return res.json()