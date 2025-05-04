from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.schemas.payment import PaymentRequest
from app.services import payment as payment_service
from app.db.session import get_db
from app.utils.verify_api_key import verify_api_key
from app.utils.app_client_info import get_metadata

router = APIRouter()

@router.post("/")
def make_payment(
    payment_in: PaymentRequest,
    db: Session = Depends(get_db),
    app_name: str = Depends(verify_api_key),
    metadata: str = Depends(get_metadata)
):
    """Make Payment"""
    metadata['app_name'] = app_name
    return payment_service.make_payment(db, payment_in, metadata)


@router.get("/verify_flutterwave_payment")
def verify_flutterwave_payment(
    tx_ref: str,
    db: Session = Depends(get_db)
):
    """Verify Flutterwave Payment Manualy"""
    return payment_service.verify_flutterwave_payment(db, tx_ref)


@router.get("/verify_stripe_payment")
def verify_stripe_payment(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Verify Stripe Payment Manualy"""
    return payment_service.verify_stripe_payment(db, session_id)


@router.get("/verify_paypal_payment")
def verify_paypal_payment(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """Verify PayPal Payment Manualy"""
    return payment_service.verify_paypal_payment(db, transaction_id)


@router.post("/webhook_flutterwave")
async def flutterwave_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Webhook to verify flutterwave payments"""
    return await payment_service.flutterwave_webhook(db, request)


@router.post("/webhook_stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Webhook to verify stripe payments"""
    return await payment_service.stripe_webhook(db, request)


@router.post("/webhook_paypal")
async def paypal_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Webhook to verify paypal payments"""
    return await payment_service.paypal_webhook(db, request)