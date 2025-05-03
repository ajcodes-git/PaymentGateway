from sqlalchemy import Column, String, Enum, DateTime, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.models import Base
import enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

class PaymentStatus(str, enum.Enum):
    PENDEING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"

class PaymentGateway(str, enum.Enum):
    STRIPE = "stripe"
    FLUTTERWAVE = "flutterwave"

class PaymentCurrency(str, enum.Enum):
    USD="usd"
    NGN="ngn"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gateway_ref = Column(String)  # tx_ref or session_id
    user_id = Column(UUID(as_uuid=True), nullable=False)
    email = Column(String, index=True)
    full_name = Column(String)
    phone_number = Column(String)
    app_source = Column(String, index=True)  # "logistics", "marketplace", etc.
    gateway = Column(Enum(PaymentGateway))
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(Enum(PaymentCurrency))
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDEING)
    description = Column(String)
    meta = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)


    def to_dict(self):
        self.meta['user_id'] = str(self.user_id)
        return {
            "id": str(self.id),
            "app_source": self.app_source,
            "gateway": self.gateway,
            "gateway_ref": self.gateway_ref,
            "amount": str(self.amount),
            "currency": self.currency,
            "status": self.status,
            "description": self.description,
            "customer": {
                "email": self.email,
                "full_name": self.full_name,
                "phone_number": self.phone_number,
            },
            "metadata": self.meta if self.meta else None,
            "created_at": str(self.created_at)
        }