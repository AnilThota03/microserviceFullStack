
import logging
from fastapi import APIRouter, HTTPException, Query
from ..services.announcement_email import (
    add_email_to_announcement_list,
    delete_email_from_announcement_list,
    get_emails_from_announcement_list
)
from ..schemas.announcement_email import AnnouncementEmailIn, AnnouncementEmailOut

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/announcement/emails",
    tags=["Announcement Email"]
)

@router.post("/")
async def add_email(body: AnnouncementEmailIn):
    logger.debug(f"[add_email] Called with email={body.email}")
    try:
        result = await add_email_to_announcement_list(email=body.email)
        logger.info(f"[add_email] Email added: {body.email}")
        return result
    except Exception as e:
        logger.error(f"[add_email] Failed to add email {body.email}: {e}")
        raise

@router.delete("/{email}")
async def delete_email(email: str):
    logger.debug(f"[delete_email] Called with email={email}")
    try:
        result = await delete_email_from_announcement_list(email)
        logger.info(f"[delete_email] Email deleted: {email}")
        return result
    except Exception as e:
        logger.error(f"[delete_email] Failed to delete email {email}: {e}")
        raise

@router.get("/")
async def get_emails():
    logger.debug("[get_emails] Called")
    try:
        result = await get_emails_from_announcement_list()
        logger.info(f"[get_emails] Fetched {len(result) if result else 0} emails")
        return result
    except Exception as e:
        logger.error(f"[get_emails] Failed to fetch emails: {e}")
        raise
