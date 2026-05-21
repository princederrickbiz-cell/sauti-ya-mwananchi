from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agents.africastalking_client import send_sms
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
