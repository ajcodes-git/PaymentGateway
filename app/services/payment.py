from sqlalchemy.orm import Session
from app.models.transaction import PaymentGateway, PaymentStatus
from app.schemas.payment import PaymentRequest
from app.repositories import transaction_repository, app_client_repository
from app.utils.response import response
from fastapi import status
from app.services.payment_providers import payment_interface, flutterwave_service, stripe_service, paypal_service
from app.services.email_provider import resend_service
from app.utils.config import settings
from typing import Type
from app.utils.email_conent import email_content
import stripe
import requests
from datetime import datetime 


def make_payment(db: Session, payment_in: PaymentRequest, metadata: dict):
    try:
        if not metadata or "app_name" not in metadata:
            return response(status.HTTP_400_BAD_REQUEST, "Missing required metadata info: 'app_name")
        
        app_source = metadata.get('app_name')
        custom = metadata.get('custom', None)
       
        app = app_client_repository.get_by_name(db, app_source)
        if not app:
            return response(status.HTTP_404_NOT_FOUND, f"{app_source} not recognized!")
        
        payment_data = payment_in.dict()
        payment_data['meta'] = custom

        payment_data['app_source'] = app_source
        transaction = transaction_repository.create(db, payment_data)

        amount = payment_in.amount
        currency = payment_in.currency
        customer_data = {
            "user_id": payment_in.user_id,
            "email": payment_in.email,
            "full_name": payment_in.full_name,
            "phone_number": payment_in.phone_number
        }
        metadata = {
            "app_name": app.name,
            "app_description": app.description if app.description else None,
            "custom": custom 
        }

        GATEWAY_SERVICES: dict[PaymentGateway, Type[payment_interface.PaymentService]] = {
            PaymentGateway.FLUTTERWAVE: flutterwave_service.FlutterwaveService,
            PaymentGateway.STRIPE: stripe_service.StripeService,
            PaymentGateway.PAYPAL: paypal_service.PayPalService
        }
        
        if payment_in.gateway not in GATEWAY_SERVICES:
            return response(status.HTTP_400_BAD_REQUEST, detail="Invalid gateway")

        service = GATEWAY_SERVICES[payment_in.gateway]()

        res = service.initiate_payment(amount, currency, transaction.id, customer_data, metadata)

        # update transaction by setting gateway_ref field
        gateway_ref = res.pop('gateway_ref')
        updated_transaction = transaction_repository.update(db, transaction, {'gateway_ref': gateway_ref})
        
        return response(
            status.HTTP_201_CREATED,
            "Payment has been initiated",
            {
                f"{payment_in.gateway.value}_response": res,
                "transaction_in_db": updated_transaction.to_dict()
            }
        )
    except Exception as e:
        return response(status_code=500, message=str(e))
    

def verify_flutterwave_payment(db: Session, tx_ref: str):
    try:
        transaction = transaction_repository.get_by_gateway_ref(db, tx_ref)
        if not transaction:
            return response(status.HTTP_404_NOT_FOUND, f"No transaction with tx_ref '{tx_ref}'")
        
        service = flutterwave_service.FlutterwaveService()
        event_dict = service.verify_payment(tx_ref)
        if not event_dict:
            return response(status.HTTP_404_NOT_FOUND, f"No transaction with tx_ref '{tx_ref}'")

        verify = event_dict.get('data')
        if verify.get('status') != 'successful':
            _ = transaction_repository.update(db, transaction, {'status': PaymentStatus.FAILED})

            # Send an email to admin and customer
            _send_email_to_admin_and_customer(
                customer=transaction.email, 
                app_source=transaction.app_source, 
                currency=transaction.currency, 
                amount=transaction.amount,
                event_body=event_dict,
                is_success=False
            )

            return response(status.HTTP_200_OK, f"Payment with tx_ref '{tx_ref}' NOT successfull!", event_dict)
        
        # payment is successfull
        _ = transaction_repository.update(db, transaction, {'status': PaymentStatus.SUCCESS})

        # Send an email to admin and customer
        _send_email_to_admin_and_customer(
            customer=transaction.email, 
            app_source=transaction.app_source, 
            currency=transaction.currency, 
            amount=transaction.amount,
            event_body=event_dict,
            is_success=True
        )

        if transaction.meta:
            webhook_body = {
                'payment_id': tx_ref,
                'is_paid': True,
                'metadata': transaction.meta
            }
            res = request_webhook_endpoint(webhook_body)

        return response(status.HTTP_200_OK, f"Payment with tx_ref '{tx_ref}' successfull. Email notification sent to both admin and customer", event_dict)
    except Exception as e:
        return response(status_code=500, message=str(e))
    

def verify_stripe_payment(db: Session, session_id: str):
    try:
        transaction = transaction_repository.get_by_gateway_ref(db, session_id)
        if not transaction:
            return response(status.HTTP_404_NOT_FOUND, f"No transaction with session_id '{session_id}'")
        
        service = stripe_service.StripeService()
        event_dict = service.verify_payment(session_id)
        if not event_dict:
            return response(status.HTTP_404_NOT_FOUND, f"No transaction with session_id '{session_id}'")

        if event_dict.get("payment_status") != 'paid':
            _ = transaction_repository.update(db, transaction, {'status': PaymentStatus.FAILED})

            # Send an email to admin and customer
            _send_email_to_admin_and_customer(
                customer=transaction.email, 
                app_source=transaction.app_source, 
                currency=transaction.currency, 
                amount=transaction.amount,
                event_body=event_dict,
                is_success=False
            )

            return response(status.HTTP_200_OK, f"Payment with session_id '{session_id}' NOT paid!", event_dict)
        
        # Payment successfull
        _ = transaction_repository.update(db, transaction, {'status': PaymentStatus.SUCCESS})

         # Send an email to admin and customer
        _send_email_to_admin_and_customer(
            customer=transaction.email, 
            app_source=transaction.app_source, 
            currency=transaction.currency, 
            amount=transaction.amount,
            event_body=event_dict,
            is_success=False
        )

        if transaction.meta:
            webhook_body = {
                'payment_id': session_id,
                'is_paid': True,
                'metadata': transaction.meta
            }
            res = request_webhook_endpoint(webhook_body)
        return response(status.HTTP_200_OK, f"Payment with session_id '{session_id}' successfull. Email notification sent to both admin and customer", event_dict)
    except Exception as e:
        return response(status_code=500, message=str(e))
    

def verify_paypal_payment(db: Session, transaction_id: str):
    try:
        transaction = transaction_repository.get_by_gateway_ref(db, transaction_id)
        if not transaction:
            return response(status.HTTP_404_NOT_FOUND, f"No transaction with transaction_id '{transaction_id}'")
        
        service = paypal_service.PayPalService()
        event_dict = service.verify_payment(transaction_id)
        if not event_dict:
            return response(status.HTTP_404_NOT_FOUND, f"No transaction with transaction_id '{transaction_id}'")

        if event_dict.get("state") != 'approved':
            _ = transaction_repository.update(db, transaction, {'status': PaymentStatus.FAILED})

            # Send an email to admin and customer
            _send_email_to_admin_and_customer(
                customer=transaction.email, 
                app_source=transaction.app_source, 
                currency=transaction.currency, 
                amount=transaction.amount,
                event_body=event_dict,
                is_success=False
            )

            return response(status.HTTP_200_OK, f"Payment with transaction_id '{transaction_id}' NOT paid!", event_dict)
        
        # Payment successfull
        _ = transaction_repository.update(db, transaction, {'status': PaymentStatus.SUCCESS})

         # Send an email to admin and customer
        _send_email_to_admin_and_customer(
            customer=transaction.email, 
            app_source=transaction.app_source, 
            currency=transaction.currency, 
            amount=transaction.amount,
            event_body=event_dict,
            is_success=False
        )

        if transaction.meta:
            webhook_body = {
                'payment_id': transaction_id,
                'is_paid': True,
                'metadata': transaction.meta
            }
            res = request_webhook_endpoint(webhook_body)
        return response(status.HTTP_200_OK, f"Payment with transaction_id '{transaction_id}' successfull. Email notification sent to both admin and customer", event_dict)
    except Exception as e:
        return response(status_code=500, message=str(e))


async def flutterwave_webhook(db: Session, request):
    try:
        print("Received webhook from flutterwave")
        event_dict = await request.json()
        print(f"Received event: {event_dict}")
        
        signature = request.headers.get("verif-hash", None)
        if not signature or signature != settings.FLW_SECRET_HASH:
            return response(status.HTTP_401_UNAUTHORIZED, "This request is not from flutterwave‼️")
        
        print("Signature verified")

        # Flutterwave sends the entire payload at root level
        payload = event_dict
        transaction_status = payload.get("status", "").lower()
        tx_ref = payload.get("txRef")
        amount = payload.get("amount")
        email = payload.get("customer", {}).get("email")

        transaction = transaction_repository.get_by_gateway_ref(db, tx_ref)
        if not transaction:
            return response(status.HTTP_404_NOT_FOUND, f"Transaction with tx_ref {tx_ref} not found")
        
        print(f"Transaction found: {transaction}")
        
        # Verify with Flutterwave API
        service = flutterwave_service.FlutterwaveService()
        result = service.verify_transaction(payload.get("id"))
        if not result:
            return

        print("Verification result: ", result)
        verify = result.get("data")
        if (
            transaction_status == "successful" and 
            transaction_status == verify.get("status", "").lower() and 
            tx_ref == verify.get("tx_ref") and 
            amount == verify.get("amount") and 
            payload.get("currency", "").lower() == verify.get("currency", "").lower()
        ):
            print("Succeeded: ", tx_ref)
            _ = transaction_repository.update(db, transaction, {'status': PaymentStatus.SUCCESS})

            print("Successful transaction updated in DB")


            _send_email_to_admin_and_customer(
                customer=transaction.email, 
                app_source=transaction.app_source, 
                currency=transaction.currency, 
                amount=transaction.amount,
                event_body=event_dict,
                is_success=True
            )

            print("Email sent to admin and customer")

            if transaction.meta:
                webhook_body = {
                    'payment_id': tx_ref,
                    'is_paid': True,
                    'metadata': transaction.meta
                }
                res = request_webhook_endpoint(webhook_body)

                print("Webhook request sent successfully: ", res)
        else:
            _ = transaction_repository.update(db, transaction, {'status': PaymentStatus.FAILED})

            _send_email_to_admin_and_customer(
                customer=transaction.email, 
                app_source=transaction.app_source, 
                currency=transaction.currency, 
                amount=transaction.amount,
                event_body=event_dict,
                is_success=False
            )
        
        print(f"[Flutterwave] 💸 Payment processed for {email} with status {transaction_status}, amount: ₦{amount}")

    except Exception as e:
        print("Error in flutterwave_webhook:", e)

    

async def stripe_webhook(db: Session, request):
    payload = await request.body()
    sig_header = request.headers.get("STRIPE_SIGNATURE")
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRPE_ENDPOINT_SECRET)

        event_dict = event.to_dict()

        intent = event_dict.get('data', {}).get('object', None)
        if not intent:
            return response(status.HTTP_400_BAD_REQUEST, "Invalid Intent")
        
        session_id = intent.get("id", None)
        if not session_id:
            return response(status.HTTP_400_BAD_REQUEST, "Invalid Session ID")
        
        transaction = transaction_repository.get_by_gateway_ref(db, session_id)
        if not transaction:
            return response(status.HTTP_404_NOT_FOUND, f"Transaction with session_id {session_id} not found")
        
        if event_dict['type'] == "payment_intent.succeeded":
            print("Succeeded: ", session_id)
            
            # update transaction
            _ = transaction_repository.update(db, transaction, {'status': PaymentStatus.SUCCESS})

            # Send an email to admin and customer
            _send_email_to_admin_and_customer(
                customer=transaction.email, 
                app_source=transaction.app_source, 
                currency=transaction.currency, 
                amount=transaction.amount,
                event_body=event_dict,
                is_success=True
            )

            if transaction.meta:
                webhook_body = {
                    'payment_id': session_id,
                    'is_paid': True,
                    'metadata': transaction.meta
                }
                res = request_webhook_endpoint(webhook_body)
        else:
            error_message = intent.get('last_payment_error', {}).get('message')
            print("Failed: ", session_id, error_message)
            
            # update transaction
            _ = transaction_repository.update(db, transaction, {'status': PaymentStatus.FAILED})

            # Send an email to admin and customer
            _send_email_to_admin_and_customer(
                customer=transaction.email, 
                app_source=transaction.app_source, 
                currency=transaction.currency, 
                amount=transaction.amount,
                event_body=event_dict,
                is_success=False
            )

        return "OK", 200
    except ValueError:
        return response(status.HTTP_400_BAD_REQUEST, "Invalid payload")
    except stripe.error.SignatureVerificationError:
        return response(status.HTTP_400_BAD_REQUEST, "Invalid signature")


async def paypal_webhook(db: Session, request):
    payload = await request.json()
    event_dict = payload.get('resource', None)
    if not event_dict:
        return response(status.HTTP_400_BAD_REQUEST, "Invalid payload")
    
    transaction_id = event_dict.get("id", None)
    if not transaction_id:
        return response(status.HTTP_400_BAD_REQUEST, "Invalid Transaction ID")
    
    transaction = transaction_repository.get_by_gateway_ref(db, transaction_id)
    if not transaction:
        return response(status.HTTP_404_NOT_FOUND, f"Transaction with transaction_id {transaction_id} not found")
    
    if event_dict['state'] == "approved":
        print("Succeeded: ", transaction_id)
        
        # update transaction
        _ = transaction_repository.update(db, transaction, {'status': PaymentStatus.SUCCESS})

        # Send an email to admin and customer
        _send_email_to_admin_and_customer(
            customer=transaction.email, 
            app_source=transaction.app_source, 
            currency=transaction.currency, 
            amount=transaction.amount,
            event_body=event_dict,
            is_success=True
        )

        if transaction.meta:
            webhook_body = {
                'payment_id': transaction_id,
                'is_paid': True,
                'metadata': transaction.meta
            }
            res = request_webhook_endpoint(webhook_body)
    else:
        print("Failed: ", transaction_id)
        
        # update transaction
        _ = transaction_repository.update(db, transaction, {'status': PaymentStatus.FAILED})

        # Send an email to admin and customer
        _send_email_to_admin_and_customer(
            customer=transaction.email, 
            app_source=transaction.app_source, 
            currency=transaction.currency, 
            amount=transaction.amount,
            event_body=event_dict,
            is_success=False
        )

    return "OK", 200


def _send_email_to_admin_and_customer(customer, app_source, currency, amount, event_body: dict, is_success: bool):
    status = 'success' if is_success else 'failure'

    # Email to admin
    _dispatch_mail(
        receiver=settings.PAYMENT_UPDATE_EMAIL, 
        app_source=app_source, 
        currency=currency, 
        amount=amount,
        event_body=event_body,
        is_admin=True,
        status=status
    )

    # Email to customer
    _dispatch_mail(
        receiver=customer, 
        app_source=app_source, 
        currency=currency, 
        amount=amount,
        event_body=event_body,
        is_admin=False,
        status=status
    )


def _dispatch_mail(receiver, app_source, currency, amount, event_body: dict, is_admin: bool, status: str):
    symbol = "₦" if currency.lower() == "ngn" else "$"
    format_context = {
        "app_source": app_source,
        "event_body": event_body,
        "amount": f"{symbol}{amount}"
    }

    sender = settings.NOREPLY_EMAIL

    role = 'admin' if is_admin else 'customer'
    content = email_content.get(status, {}).get(role)

    if not content:
        raise ValueError(f"Invalid email status '{status}' or role '{role}'")

    subject = content["subject"].format(**format_context)
    formatted_body = content["body"].format(**format_context)

    return resend_service.send_email(sender, receiver, subject, formatted_body)


def request_webhook_endpoint(webhook_body):
    headers = {
        #"Authorization": f"Bearer {settings.DOOS_CORP_PAYMENT_GATEWAY_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    url = webhook_body.get('metadata', {}).get('webhook_url', None)
    if not url:
        return
    
    print(f"Sending payment info to webhook endpoint: {url}")
    
    webhook_body['metadata']['payment_timestamp'] = str(datetime.now())
    res = requests.post(
        url=url,
        headers=headers,
        json=webhook_body
    )
    res.raise_for_status()
    
    result = res.json()
    print(f"Webhook request sent successfully: {result}")
    return result