from fastapi import FastAPI
from pydantic import BaseModel
import aiosmtplib
from email.message import EmailMessage
import os

app = FastAPI(title="Mail Service")

from typing import Optional

class MailRequest(BaseModel):
    to: str
    subject: str
    html: Optional[str] = None
    text: Optional[str] = None

@app.post("/send-mail/")
async def send_mail(request: MailRequest):
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    if not EMAIL_USER or not EMAIL_PASSWORD:
        return {"success": False, "error": "Email credentials not set in environment."}

    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = request.to
    msg["Subject"] = request.subject

    if request.html:
        msg.set_content(request.text or "This is a fallback plain text message.")
        msg.add_alternative(request.html, subtype="html")
    elif request.text:
        msg.set_content(request.text)
    else:
        return {"success": False, "error": "Either 'html' or 'text' must be provided."}

    try:
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=465,
            username=EMAIL_USER,
            password=EMAIL_PASSWORD,
            use_tls=True,
            timeout=20
        )
        return {"success": True, "message": "Email sent successfully"}
    except aiosmtplib.SMTPException as e:
        return {"success": False, "error": f"SMTP error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"General error: {str(e)}"}
