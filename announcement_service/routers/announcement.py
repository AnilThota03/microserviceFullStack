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

router = APIRouter(
    prefix="/api/announcement",
    tags=["Announcements"]
)

@router.post("/", response_model=dict)
async def insert_announcement_route(announcement: AnnouncementCreate):
    result = await insert_announcement(announcement)
    return {"message": "Announcement created successfully", "data": result}

@router.get("/", response_model=dict)
async def get_announcements_route():
    result = await get_announcements()
    return {"message": "Announcements fetched successfully", "data": result}

@router.get("/{id}", response_model=dict)
async def get_announcement_by_id_route(id: str):
    result = await get_announcement_by_id(id)
    return {"message": "Announcement fetched successfully", "data": result}

@router.put("/{id}", response_model=dict)
async def update_announcement_route(id: str, announcement: AnnouncementCreate):
    result = await update_announcement(id, announcement)
    return {"message": "Announcement updated successfully", "data": result}

@router.delete("/{id}", response_model=dict)
async def delete_announcement_route(id: str):
    await delete_announcement(id)
    return {"message": "Announcement deleted successfully"}
