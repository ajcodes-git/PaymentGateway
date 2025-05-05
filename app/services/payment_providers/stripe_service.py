import stripe
from decimal import Decimal
from .payment_interface import PaymentService
from typing import Optional
from app.utils.config import settings  # Assuming you store secrets here
import json

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService(PaymentService):
    def initiate_payment(self, amount: Decimal, currency: str, transaction_id, customer: dict, metadata: Optional[dict] = None):
        if not customer or "email" not in customer:
            raise ValueError("Missing required customer info")

        amount_in_cents = int(amount * 100)

        print(f"Stripe Payment: {amount_in_cents} cents for {currency} to {customer['email']}")

        # Use Stripe Checkout Session with multiple payment methods enabled
        session = stripe.checkout.Session.create(
            payment_method_types=["card", "us_bank_account"], 
            line_items=[{
                "price_data": {
                    "currency": currency.lower(),
                    "product_data": {
                        "name": metadata.get("app_name", "DoosCorp Apps"),
                        "description": metadata.get("app_description", "An app owned by DoosCorp")
                    },
                    "unit_amount": amount_in_cents,
                },
                "quantity": 1,
            }],
            mode="payment",
            customer_email=customer.get("email"),
            success_url="https://yourapp.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://yourapp.com/cancel",
            metadata={
                "user_id": customer.get("id"),
                "transaction_id": transaction_id,
                "custom": json.dumps(metadata.get("custom", None))
            }
        )

        return {"payment_link": session.url, "gateway_ref": session.id}
    
    def verify_payment(self, session_id: str):
        session = stripe.checkout.Session.retrieve(session_id)
        if not session:
            return {}

        session['amount_total'] = session.get("amount_total") / 100  # Convert from cents
        return session
