from ..models.announcement_email import get_announcement_email_collection
from ..schemas.announcement_email import AnnouncementEmailModel
from fastapi import HTTPException
from datetime import datetime
from pymongo.errors import DuplicateKeyError
import httpx
import os

from typing import Optional

async def add_email_to_announcement_list(email: str, user_id: Optional[str] = None):
    collection = get_announcement_email_collection()
    existing = await collection.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already subscribed")
    data = AnnouncementEmailModel(
        email=email,
        userId=user_id,
        subscribed=True,
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow(),
    ).dict(by_alias=True)
    try:
        await collection.insert_one(data)
        # Send mail via mail microservice
        MAIL_SERVICE_URL = os.getenv("MAIL_SERVICE_URL", "http://localhost:8001/send-mail/")
        FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
        async with httpx.AsyncClient() as client:
            payload = {
                "to": email,
                "subject": "Subscribed to PDIT Announcements",
                "text": f"You have successfully subscribed to PDIT Announcements. If you want to unsubscribe, please click this link: {FRONTEND_URL}/unsubscribe/{email}"
            }
            await client.post(MAIL_SERVICE_URL, json=payload)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Email already exists")
    return {"message": "Email added to announcement list"}

async def delete_email_from_announcement_list(email: str):
    collection = get_announcement_email_collection()
    result = await collection.delete_one({"email": email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Email not found")
    return {"message": "Unsubscribed from PDIT"}

async def get_emails_from_announcement_list():
    collection = get_announcement_email_collection()
    emails = []
    async for doc in collection.find({}):
        emails.append({
            "email": doc.get("email"),
            "user_id": str(doc.get("userId")) if doc.get("userId") else None,
            "subscribed": doc.get("subscribed", False),
            "created_at": doc.get("createdAt"),
            "updated_at": doc.get("updatedAt"),
            "id": str(doc.get("_id")),
        })
    return {"emails": emails}
