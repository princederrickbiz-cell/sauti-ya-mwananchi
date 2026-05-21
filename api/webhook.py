from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agents.africastalking_client import send_sms
from agents.msaidizi import route
from agents.mwenza import handle_ussd
from agents.settings import ROOT_DIR


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


@app.post("/message")
def message(payload: MessageRequest):
    return {"reply": route(phone=payload.phone, message=payload.message)}


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
