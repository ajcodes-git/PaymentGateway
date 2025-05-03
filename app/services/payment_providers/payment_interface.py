from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional

class PaymentService(ABC):
    @abstractmethod
    def initiate_payment(self, amount: Decimal, currency: str, customer: dict, metadata: Optional[dict] = None):
       """Initiate a payment"""
       pass
    
    @abstractmethod
    def verify_payment(self, transaction_id: str) -> dict:
        """Verify a payment by its transaction reference"""
        pass