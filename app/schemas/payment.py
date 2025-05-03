from pydantic import BaseModel, EmailStr
from decimal import Decimal
from typing import Optional
from app.models.transaction import PaymentCurrency, PaymentGateway

class PaymentRequest(BaseModel):
    amount: Decimal
    currency: PaymentCurrency
    gateway: PaymentGateway
    user_id: str
    email: EmailStr
    full_name: Optional[str]
    phone_number: Optional[str]
    description: Optional[str]