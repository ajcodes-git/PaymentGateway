import requests
from decimal import Decimal
from typing import Optional
from app.utils.config import settings
from .payment_interface import PaymentService
import json
import random
import string


class FlutterwaveService(PaymentService):
    def initiate_payment(self, amount: Decimal, currency: str, transaction_id, customer: dict, metadata: Optional[dict] = None):
        if not customer or "email" not in customer:
            raise ValueError("Missing required customer info")
        
        amount_in_naira = self.get_usd_to_ngn_conversion(amount)
        
        tx_ref = self.generate_tx_ref()

        res = requests.post(
            "https://api.flutterwave.com/v3/payments",
            headers={
                "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "tx_ref": tx_ref,
                "amount": amount_in_naira if amount_in_naira else float(amount),
                "currency": "NGN",
                "redirect_url": "https://yourapp.com/flw-redirect",
                "payment_options": 'card, ussd, account, banktransfer, opay',
                "customer": {
                    "email": customer.get("email"),
                    "name": customer.get("full_name", None),
                    "phonenumber": customer.get("phone_number", None),
                },
                "customizations": {
                    "title": metadata.get("app_name", "DoosCorp Apps"),
                    "description": metadata.get("app_description", "An app owned by DoosCorp"),
                },
                "max_retry_attempt": 5,
                "meta": {
                    "user_id": str(customer.get("id")),
                    "transaction_id": str(transaction_id),
                    "custom": metadata.get("custom", None)
                }
            }
        )
        return {"res": res.json(), "gateway_ref": tx_ref}
    
    def verify_payment(self, tx_ref: str) -> dict:
        url = f"https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref={tx_ref}"
        res = requests.get(
            url=url,
            headers={
                "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
                "Content-Type": "application/json"
            }
        )
        result = res.json()
        if result.get("status") != "success":
            return {}
        
        return result
    
    def verify_transaction(self, transaction_id) -> dict:
        res = requests.get(
            f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
                "Content-Type": "application/json"
            }
        )
        result = res.json()
        if result.get('status') != "success":
            return {}
        
        return result
    
    def get_usd_to_ngn_conversion(self, amount: float, source_currency: str = "NGN", destination_currency: str = "USD"):
        url = "https://api.flutterwave.com/v3/transfers/rates"
    
        headers = {
            "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        print("CONVERSION HEADERS: ", headers)

        params = {
            "amount": amount,
            "source_currency": source_currency,
            "destination_currency": destination_currency
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  
            result = response.json()
            if not result:
                return None
            
            print("CONVERSION RESULT: ", result)
            data = result.get('data', None)
            return data.get('source', {}).get('amount') if data else None
        except requests.exceptions.RequestException as e:
            print(f"Error making request to Flutterwave API: {e}")
            return None
    
    def generate_tx_ref(self):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choices(characters, k=64))
    
