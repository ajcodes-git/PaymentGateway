import resend
from typing import List, Union
from app.utils.config import settings

resend.api_key = settings.RESEND_API_KEY

def send_email(
    sender_email: str,
    recipient_email: Union[str, List[str]],
    subject: str,
    body: str
):
    response = None 

    if isinstance(recipient_email, str):
        params: resend.Emails.SendParams = {
            "from": f"Dooscorp <{sender_email}>",
            "to": [str(recipient_email)],
            "subject": subject,
            "html": f"<p>{body}</p>"
        }
        response = resend.Emails.send(params)

    elif isinstance(recipient_email, list):
        batch_params: List[resend.Emails.SendParams] = [
            {
                "from": f"Acme <{sender_email}>",
                "to": [str(email)],
                "subject": subject,
                "html": f"<p>{body}</p>"
            }
            for email in recipient_email
        ]
        response = resend.Batch.send(batch_params)

    print("Email Response: ", response)
    return response
