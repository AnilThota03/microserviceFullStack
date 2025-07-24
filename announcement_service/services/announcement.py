from ..models.announcement import get_announcement_collection
from ..schemas.announcement import AnnouncementCreate, AnnouncementOut
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime

async def insert_announcement(announcement: AnnouncementCreate):
    announcements = get_announcement_collection()
    ann_dict = announcement.dict()
    ann_dict["created_at"] = datetime.utcnow()
    ann_dict["updated_at"] = datetime.utcnow()
    result = await announcements.insert_one(ann_dict)
    ann_dict["_id"] = result.inserted_id
    return AnnouncementOut(**ann_dict)

async def get_announcements():
    announcements = get_announcement_collection()
    result = []
    async for ann in announcements.find({}).sort("created_at", -1):
        ann["id"] = str(ann["_id"])
        result.append(AnnouncementOut(**ann))
    return result

async def get_announcement_by_id(id: str):
    announcements = get_announcement_collection()
    ann = await announcements.find_one({"_id": ObjectId(id)})
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    ann["id"] = str(ann["_id"])
    return AnnouncementOut(**ann)

async def update_announcement(id: str, announcement: AnnouncementCreate):
    announcements = get_announcement_collection()
    update_data = announcement.dict()
    update_data["updated_at"] = datetime.utcnow()
    updated = await announcements.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": update_data},
        return_document=True
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Announcement not found")
    updated["id"] = str(updated["_id"])
    return AnnouncementOut(**updated)

async def delete_announcement(id: str):
    announcements = get_announcement_collection()
    result = await announcements.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"message": "Announcement deleted successfully"}
