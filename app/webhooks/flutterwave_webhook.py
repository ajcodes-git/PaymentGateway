from fastapi import APIRouter, Request, HTTPException
import hmac
import hashlib
import os

router = APIRouter()

FLW_SECRET_HASH = "your_webhook_hash_key"  # From Flutterwave dashboard

@router.post("/webhook/flutterwave")
async def flutterwave_webhook(request: Request):
    body = await request.json()
    signature = request.headers.get("verif-hash")

    if not signature or signature != FLW_SECRET_HASH:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event = body.get("event")

    if event == "charge.completed" or event == "transfer.completed":
        tx_ref = body["data"]["tx_ref"]
        email = body["data"]["customer"]["email"]
        amount = body["data"]["amount"]

        # TODO: Lookup tx_ref / email and update DB
        print(f"[Flutterwave] 💸 Payment confirmed for {email}, amount: ₦{amount}")

    return {"status": "received"}
