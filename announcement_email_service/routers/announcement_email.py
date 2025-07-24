from fastapi import APIRouter, HTTPException, Query
from ..services.announcement_email import (
    add_email_to_announcement_list,
    delete_email_from_announcement_list,
    get_emails_from_announcement_list
)
from ..schemas.announcement_email import AnnouncementEmailIn, AnnouncementEmailOut

router = APIRouter(
    prefix="/api/announcement/emails",
    tags=["Announcement Email"]
)

@router.post("/")
async def add_email(body: AnnouncementEmailIn):
    return await add_email_to_announcement_list(email=body.email)

@router.delete("/{email}")
async def delete_email(email: str):
    return await delete_email_from_announcement_list(email)

@router.get("/")
async def get_emails():
    return await get_emails_from_announcement_list()
