import aiosmtplib
from email.message import EmailMessage
import os
from decouple import config
from typing import Optional

async def send_mail(
    to: str,
    subject: str,
    text: Optional[str] = None,
    html: Optional[str] = None
) -> dict:
    EMAIL_USER = str(os.getenv("MAIL_USERNAME") or config("MAIL_USERNAME", default=""))
    EMAIL_PASSWORD = str(os.getenv("MAIL_PASSWORD") or config("MAIL_PASSWORD", default=""))
    SMTP_HOST = str(os.getenv("MAIL_SERVER") or config("MAIL_SERVER", default="smtp.example.com"))
    SMTP_PORT = int(os.getenv("MAIL_PORT") or config("MAIL_PORT", default=465))
    if not EMAIL_USER or not EMAIL_PASSWORD:
        return {"success": False, "error": "Email credentials not set in environment."}

    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = to
    msg["Subject"] = subject

    if html:
        msg.set_content(text or "This is a fallback plain text message.")
        msg.add_alternative(html, subtype="html")
    elif text:
        msg.set_content(text)
    else:
        return {"success": False, "error": "Either 'html' or 'text' must be provided."}

    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
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
