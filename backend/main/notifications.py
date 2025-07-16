from fastapi import APIRouter, Body
from config import config
from pydantic import BaseModel, EmailStr
from typing import Optional
import smtplib
from email.mime.text import MIMEText
import ssl
from twilio.rest import Client as TwilioClient

router = APIRouter()

class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str

class SMSRequest(BaseModel):
    to: str  # E.164 phone number
    body: str

@router.post("/email")
def send_email(req: EmailRequest):
    try:
        msg = MIMEText(req.body, "html")
        msg["Subject"] = req.subject
        msg["From"] = config.EMAIL_USER
        msg["To"] = req.to

        context = ssl.create_default_context()
        with smtplib.SMTP(config.EMAIL_HOST, config.EMAIL_PORT) as server:
            server.starttls(context=context)
            server.login(config.EMAIL_USER, config.EMAIL_PASSWORD)
            server.sendmail(config.EMAIL_USER, [req.to], msg.as_string())
        return {"msg": f"Email sent to {req.to}"}
    except Exception as e:
        return {"error": str(e)}

@router.post("/sms")
def send_sms(req: SMSRequest):
    try:
        client = TwilioClient(config.TWILIO_SID, config.TWILIO_TOKEN)
        message = client.messages.create(
            body=req.body,
            from_=config.TWILIO_FROM,
            to=req.to
        )
        return {"msg": f"SMS sent to {req.to}", "sid": message.sid}
    except Exception as e:
        return {"error": str(e)}
