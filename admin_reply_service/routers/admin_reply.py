
import logging
from fastapi import APIRouter, HTTPException
from ..schemas.admin_reply import AdminReplyCreate, AdminReplyOut
from ..services.admin_reply import create_reply #, get_ticket_and_replies
from typing import List

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin-replies", tags=["Admin Replies"])

@router.post("/", response_model=AdminReplyOut)
async def create_reply_route(reply: AdminReplyCreate):
    logger.debug(f"[create_reply_route] Called with reply={reply}")
    try:
        result = await create_reply(reply)
        logger.info("[create_reply_route] Admin reply created successfully")
        return result
    except Exception as e:
        logger.error(f"[create_reply_route] Failed to create admin reply: {e}")
        raise

# @router.get("/{ticket_id}", response_model=TicketWithReplies)
# async def get_ticket_and_replies_route(ticket_id: str):
#     result = await get_ticket_and_replies(ticket_id)
#     return result
