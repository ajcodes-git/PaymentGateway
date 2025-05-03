import stripe
from fastapi import APIRouter, Request, Header, HTTPException

router = APIRouter()

stripe.api_key = "sk_test_..."
STRIPE_ENDPOINT_SECRET = "whsec_..."

@router.post("/webhook/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, convert_underscores=False),
):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload=payload.decode(),
            sig_header=stripe_signature,
            secret=STRIPE_ENDPOINT_SECRET,
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session["customer_email"]
        amount = session["amount_total"] / 100

        # TODO: Lookup user by email and update DB
        print(f"[Stripe] 💸 Payment successful from {email} for ${amount}")

    return {"status": "received"}
