from ..models.announcement_email import get_announcement_email_collection
from ..schemas.announcement_email import AnnouncementEmailModel
from fastapi import HTTPException
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from ..services.mail_sender import mail_sender_service
from bson import ObjectId
from config import settings

async def add_email_to_announcement_list(email: str, user_id: str = None):
    collection = get_announcement_email_collection()
    existing = await collection.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already subscribed")
    data = AnnouncementEmailModel(
        email=email,
        user_id=user_id,
        subscribed=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    ).dict(by_alias=True)
    try:
        await collection.insert_one(data)
        await mail_sender_service(
            to=email,
            subject="Subscribed to PDIT Announcements",
            text=f"You have successfully subscribed to PDIT Announcements. If you want to unsubscribe, please click this link: {settings.FRONTEND_URL}/unsubscribe/{email}",
        )
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
            "user_id": str(doc.get("user_id")) if doc.get("user_id") else None,
            "subscribed": doc.get("subscribed", False),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
            "id": str(doc.get("_id")),
        })
    return {"emails": emails}
