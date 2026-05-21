import json
import logging
from datetime import datetime
from time import sleep
from typing import Dict, List, Optional

import requests

from agents.settings import (
    AFRICASTALKING_API_KEY,
    AFRICASTALKING_SENDER_ID,
    AFRICASTALKING_USERNAME,
    ROOT_DIR,
)

logger = logging.getLogger(__name__)

SMS_URL = "https://api.africastalking.com/version1/messaging"
WHATSAPP_URL = "https://api.africastalking.com/version1/messaging"
MESSAGE_LOG_FILE = ROOT_DIR / "data" / "message_log.jsonl"


def _ensure_log_file():
    """Ensure message log file exists."""
    MESSAGE_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def _log_message(phone: str, message: str, channel: str, status: str, response: Optional[Dict] = None):
    """Log message delivery to file."""
    _ensure_log_file()
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "phone": phone,
        "channel": channel,
        "message_length": len(message),
        "status": status,
        "response": response,
    }
    try:
        with open(MESSAGE_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        logger.error(f"Failed to log message: {e}")


def send_sms(to: str, message: str, retries: int = 3) -> Dict:
    """Send SMS through Africa's Talking with retry logic."""
    if not AFRICASTALKING_API_KEY:
        _log_message(to, message, "sms", "failed", {"reason": "Missing API key"})
        return {
            "sent": False,
            "channel": "sms",
            "reason": "Missing AFRICASTALKING_API_KEY in .env",
        }

    payload = {
        "username": AFRICASTALKING_USERNAME,
        "to": to,
        "message": message,
    }
    if AFRICASTALKING_SENDER_ID:
        payload["from"] = AFRICASTALKING_SENDER_ID

    headers = {
        "apiKey": AFRICASTALKING_API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(SMS_URL, headers=headers, data=payload, timeout=20)
            response.raise_for_status()
            result = response.json()
            _log_message(to, message, "sms", "success", result)
            return {
                "sent": True,
                "channel": "sms",
                "response": result,
            }
        except requests.exceptions.RequestException as e:
            logger.warning(f"SMS send attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                sleep(2 ** attempt)  # Exponential backoff: 2s, 4s, 8s
            else:
                _log_message(to, message, "sms", "failed", {"error": str(e), "attempts": retries})
                return {
                    "sent": False,
                    "channel": "sms",
                    "reason": f"Failed after {retries} attempts",
                    "error": str(e),
                }


def send_whatsapp(to: str, message: str, retries: int = 3) -> Dict:
    """Send WhatsApp message through Africa's Talking with retry logic."""
    if not AFRICASTALKING_API_KEY:
        _log_message(to, message, "whatsapp", "failed", {"reason": "Missing API key"})
        return {
            "sent": False,
            "channel": "whatsapp",
            "reason": "Missing AFRICASTALKING_API_KEY in .env",
        }

    payload = {
        "username": AFRICASTALKING_USERNAME,
        "to": to,
        "message": message,
    }

    headers = {
        "apiKey": AFRICASTALKING_API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(WHATSAPP_URL, headers=headers, data=payload, timeout=20)
            response.raise_for_status()
            result = response.json()
            _log_message(to, message, "whatsapp", "success", result)
            return {
                "sent": True,
                "channel": "whatsapp",
                "response": result,
            }
        except requests.exceptions.RequestException as e:
            logger.warning(f"WhatsApp send attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                sleep(2 ** attempt)
            else:
                _log_message(to, message, "whatsapp", "failed", {"error": str(e), "attempts": retries})
                return {
                    "sent": False,
                    "channel": "whatsapp",
                    "reason": f"Failed after {retries} attempts",
                    "error": str(e),
                }


def send_message(to: str, message: str, channel: str = "sms") -> Dict:
    """Send message via SMS or WhatsApp."""
    if channel.lower() == "whatsapp":
        return send_whatsapp(to, message)
    else:
        return send_sms(to, message)
