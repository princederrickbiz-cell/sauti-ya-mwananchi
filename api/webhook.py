from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agents.africastalking_client import send_sms, send_whatsapp, send_message
from agents.message_queue import (
    add_to_queue,
    process_queue,
    get_queue_status,
    clear_queue,
    load_queue_from_file,
)
from agents.msaidizi import route
from agents.mwenza import handle_ussd
from agents.settings import ROOT_DIR
from agents.vision import check_image


app = FastAPI(title="Sauti ya Mwananchi")
app.mount("/static", StaticFiles(directory=ROOT_DIR / "static"), name="static")


class MessageRequest(BaseModel):
    phone: str = "+254700000000"
    message: str


class UssdRequest(BaseModel):
    session_id: str = "demo-session"
    phone: str = "+254700000000"
    text: str = ""


class BulkMessageRequest(BaseModel):
    recipients: list[str]
    message: str
    channel: str = "sms"


class ChannelMessageRequest(BaseModel):
    phone: str
    message: str
    channel: str = "sms"


@app.get("/")
def ui():
    return FileResponse(ROOT_DIR / "static" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "service": "Sauti ya Mwananchi"}


@app.get("/about")
def about():
    return {
        "service": "Sauti ya Mwananchi",
        "agents": ["Msaidizi", "Mwalimu", "Kiongozi", "Ukweli", "Mwenza"],
        "data_source": "IEBC public registration-centre page exported to data/polling_stations.csv",
        "guardrails": [
            "politically neutral",
            "cite trusted civic sources",
            "return Unverified when unsupported",
            "do not store voter ID data",
        ],
    }


@app.post("/message")
def message(payload: MessageRequest):
    return {"reply": route(phone=payload.phone, message=payload.message)}


@app.post("/fact-check/image")
async def fact_check_image(
    image: UploadFile = File(...),
    claim_hint: str = Form(""),
):
    image_bytes = await image.read()
    return {
        "filename": image.filename,
        "mime_type": image.content_type,
        "reply": check_image(
            image_bytes=image_bytes,
            mime_type=image.content_type or "",
            claim_hint=claim_hint,
        ),
    }


@app.post("/ussd")
def ussd(payload: UssdRequest):
    return {
        "reply": handle_ussd(
            session_id=payload.session_id,
            phone=payload.phone,
            text=payload.text,
        )
    }


@app.post("/africastalking/sms")
def africastalking_sms(
    from_: str = Form(..., alias="from"),
    text: str = Form(...),
):
    reply = route(phone=from_, message=text)
    delivery = send_sms(to=from_, message=reply)
    return {"reply": reply, "delivery": delivery}


@app.post("/africastalking/ussd")
def africastalking_ussd(
    sessionId: str = Form(...),
    phoneNumber: str = Form(...),
    text: str = Form(""),
):
    return handle_ussd(session_id=sessionId, phone=phoneNumber, text=text)


# Direct SMS/WhatsApp endpoints with channel support
@app.post("/send-sms")
def send_sms_endpoint(payload: MessageRequest):
    """Send SMS directly (requires Africa's Talking credentials)."""
    result = send_sms(to=payload.phone, message=payload.message)
    return result


@app.post("/send-whatsapp")
def send_whatsapp_endpoint(payload: MessageRequest):
    """Send WhatsApp message directly (requires Africa's Talking credentials)."""
    result = send_whatsapp(to=payload.phone, message=payload.message)
    return result


@app.post("/send-message")
def send_message_endpoint(payload: ChannelMessageRequest):
    """Send message via SMS or WhatsApp (channel: 'sms' or 'whatsapp')."""
    result = send_message(to=payload.phone, message=payload.message, channel=payload.channel)
    return result


# Bulk messaging and queue management endpoints
@app.post("/bulk-message/add")
def bulk_message_add(payload: BulkMessageRequest):
    """Add messages to queue for bulk sending."""
    return add_to_queue(
        recipients=payload.recipients,
        message=payload.message,
        channel=payload.channel,
    )


@app.post("/bulk-message/process")
def bulk_message_process(max_items: int = None):
    """Process pending messages in queue."""
    return process_queue(max_items=max_items)


@app.get("/bulk-message/status")
def bulk_message_status():
    """Get status of message queue."""
    return get_queue_status()


@app.post("/bulk-message/clear")
def bulk_message_clear():
    """Clear all pending messages from queue."""
    return clear_queue()


@app.post("/bulk-message/load")
def bulk_message_load():
    """Load pending messages from file."""
    return load_queue_from_file()
