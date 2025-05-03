email_content = {
    "success": {
        "admin": {
            "subject": "Payment received for {app_source}",
            "body": (
                "Hello Admin,\n\n"
                "A payment of {amount} has been successfully processed for {app_source}. "
                "See transaction details below:\n\n"
                "{event_body}\n\n"
                "Keep record accordingly.\n\n"
                "Regards,\n"
                "Dooscorp Payment System"
            )
        },
        "customer": {
            "subject": "Your payment for {app_source} has been confirmed",
            "body": (
                "Hello,\n\n"
                "We’ve successfully received your payment of {amount} for {app_source}. "
                "Thank you for trusting Dooscorp with your service needs.\n\n"
                "If you have any questions, feel free to reply to this email.\n\n"
                "Best regards,\n"
                "Dooscorp Team"
            )
        }
    },
    "failure": {
        "admin": {
            "subject": "Payment failed for {app_source}",
            "body": (
                "Hello Admin,\n\n"
                "A payment attempt for {app_source} has failed. Below are the event details for logging "
                "and possible investigation:\n\n"
                "{event_body}\n\n"
                "Follow up if necessary.\n\n"
                "Regards,\n"
                "Dooscorp Payment System"
            )
        },
        "customer": {
            "subject": "Your payment for {app_source} was not successful",
            "body": (
                "Hello,\n\n"
                "Unfortunately, your payment of {amount} for {app_source} could not be confirmed at this time. "
                "This might be due to a network issue, card decline, or incomplete authorization.\n\n"
                "Please try again or check with your bank. You may also wait 24 hours and verify the payment status.\n\n"
                "If this was not expected, feel free to contact support.\n\n"
                "Regards,\n"
                "Dooscorp Team"
            )
        }
    }
}
