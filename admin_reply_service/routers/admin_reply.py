from fastapi import APIRouter, HTTPException
from ..schemas.admin_reply import AdminReplyCreate, AdminReplyOut
from ..services.admin_reply import create_reply #, get_ticket_and_replies
from typing import List

router = APIRouter(prefix="/api/admin-replies", tags=["Admin Replies"])

@router.post("/", response_model=AdminReplyOut)
async def create_reply_route(reply: AdminReplyCreate):
    result = await create_reply(reply)
    return result

# @router.get("/{ticket_id}", response_model=TicketWithReplies)
# async def get_ticket_and_replies_route(ticket_id: str):
#     result = await get_ticket_and_replies(ticket_id)
#     return result
