from ..models.admin_reply import get_admin_reply_collection
from ..schemas.admin_reply import AdminReplyCreate, AdminReplyOut
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime

async def create_reply(reply: AdminReplyCreate):
    replies = get_admin_reply_collection()
    now = datetime.utcnow()
    reply_dict = reply.dict(by_alias=True)
    reply_dict["createdAt"] = now
    reply_dict["updatedAt"] = now
    result = await replies.insert_one(reply_dict)
    reply_dict["_id"] = result.inserted_id
    return AdminReplyOut(**reply_dict)

async def get_ticket_and_replies(ticket_id: str):
    replies = get_admin_reply_collection()
    result = []
    async for reply in replies.find({"ticketId": ticket_id}):
        reply["id"] = str(reply["_id"])
        result.append(AdminReplyOut(**reply))
    return result
