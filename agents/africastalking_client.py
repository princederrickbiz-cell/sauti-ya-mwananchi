import requests

from agents.settings import (
    AFRICASTALKING_API_KEY,
    AFRICASTALKING_SENDER_ID,
    AFRICASTALKING_USERNAME,
)


SMS_URL = "https://api.africastalking.com/version1/messaging"


def send_sms(to, message):
    """Send an SMS through Africa's Talking if credentials are configured."""
    if not AFRICASTALKING_API_KEY:
        return {
            "sent": False,
            "reason": "Missing AFRICASTALKING_API_KEY in .env",
        }

    payload = {
        "username": AFRICASTALKING_USERNAME,
        "to": to,
        "message": message,
    }
    if AFRICASTALKING_SENDER_ID:
        payload["from"] = AFRICASTALKING_SENDER_ID

    response = requests.post(
        SMS_URL,
        headers={
            "apiKey": AFRICASTALKING_API_KEY,
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data=payload,
        timeout=20,
    )
    response.raise_for_status()
    return {
        "sent": True,
        "response": response.json(),
    }
