
import logging
from fastapi import APIRouter, HTTPException
from ..schemas.announcement import AnnouncementCreate, AnnouncementOut
from ..services.announcement import (
    insert_announcement,
    get_announcements,
    get_announcement_by_id,
    update_announcement,
    delete_announcement,
)
from typing import List

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/announcement",
    tags=["Announcements"]
)

@router.post("/", response_model=dict)
async def insert_announcement_route(announcement: AnnouncementCreate):
    logger.debug(f"[insert_announcement_route] Called with announcement={announcement}")
    try:
        result = await insert_announcement(announcement)
        logger.info("[insert_announcement_route] Announcement created successfully")
        return {"message": "Announcement created successfully", "data": result}
    except Exception as e:
        logger.error(f"[insert_announcement_route] Failed to create announcement: {e}")
        raise

@router.get("/", response_model=dict)
async def get_announcements_route():
    logger.debug("[get_announcements_route] Called")
    try:
        result = await get_announcements()
        logger.info(f"[get_announcements_route] Fetched {len(result) if result else 0} announcements")
        return {"message": "Announcements fetched successfully", "data": result}
    except Exception as e:
        logger.error(f"[get_announcements_route] Failed to fetch announcements: {e}")
        raise

@router.get("/{id}", response_model=dict)
async def get_announcement_by_id_route(id: str):
    logger.debug(f"[get_announcement_by_id_route] Called with id={id}")
    try:
        result = await get_announcement_by_id(id)
        logger.info(f"[get_announcement_by_id_route] Announcement fetched for id={id}")
        return {"message": "Announcement fetched successfully", "data": result}
    except Exception as e:
        logger.error(f"[get_announcement_by_id_route] Failed to fetch announcement {id}: {e}")
        raise

@router.put("/{id}", response_model=dict)
async def update_announcement_route(id: str, announcement: AnnouncementCreate):
    logger.debug(f"[update_announcement_route] Called with id={id}, announcement={announcement}")
    try:
        result = await update_announcement(id, announcement)
        logger.info(f"[update_announcement_route] Announcement updated for id={id}")
        return {"message": "Announcement updated successfully", "data": result}
    except Exception as e:
        logger.error(f"[update_announcement_route] Failed to update announcement {id}: {e}")
        raise

@router.delete("/{id}", response_model=dict)
async def delete_announcement_route(id: str):
    logger.debug(f"[delete_announcement_route] Called with id={id}")
    try:
        await delete_announcement(id)
        logger.info(f"[delete_announcement_route] Announcement deleted for id={id}")
        return {"message": "Announcement deleted successfully"}
    except Exception as e:
        logger.error(f"[delete_announcement_route] Failed to delete announcement {id}: {e}")
        raise
