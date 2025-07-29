
import logging
from fastapi import APIRouter
from ..schemas.support_ticket import SupportTicketCreate, SupportTicketOut, SupportTicketUpdate
from ..services.support_ticket import (
    create_support_ticket,
    get_support_tickets,
    get_support_ticket_by_id,
    update_support_ticket,
    delete_support_ticket,
    get_tickets_by_status
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/support-ticket",
    tags=["Support Tickets"]
)

@router.post("/", response_model=dict)
async def create_support_ticket_route(ticket: SupportTicketCreate):
    logger.debug(f"[create_support_ticket_route] Called with ticket={ticket}")
    try:
        result = await create_support_ticket(ticket)
        logger.info(f"[create_support_ticket_route] Support ticket created for {ticket.email if hasattr(ticket, 'email') else 'unknown email'}")
        return {"message": "Support ticket created successfully", "data": result}
    except Exception as e:
        logger.error(f"[create_support_ticket_route] Failed to create support ticket: {e}")
        raise

@router.get("/", response_model=dict)
async def get_support_tickets_route():
    logger.debug("[get_support_tickets_route] Called")
    try:
        result = await get_support_tickets()
        logger.info(f"[get_support_tickets_route] Fetched {len(result) if result else 0} tickets")
        return {"message": "Support tickets fetched successfully", "data": result}
    except Exception as e:
        logger.error(f"[get_support_tickets_route] Failed to fetch tickets: {e}")
        raise

@router.get("/{ticket_id}", response_model=dict)
async def get_support_ticket_by_id_route(ticket_id: str):
    logger.debug(f"[get_support_ticket_by_id_route] Called with ticket_id={ticket_id}")
    try:
        result = await get_support_ticket_by_id(ticket_id)
        logger.info(f"[get_support_ticket_by_id_route] Ticket fetched for id={ticket_id}")
        return {"message": "Support ticket fetched successfully", "data": result}
    except Exception as e:
        logger.error(f"[get_support_ticket_by_id_route] Failed to fetch ticket {ticket_id}: {e}")
        raise

@router.patch("/{ticket_id}", response_model=dict)
async def update_support_ticket_route(ticket_id: str, body: SupportTicketUpdate):
    logger.debug(f"[update_support_ticket_route] Called with ticket_id={ticket_id}, body={body}")
    try:
        result = await update_support_ticket(ticket_id, body)
        logger.info(f"[update_support_ticket_route] Ticket updated for id={ticket_id}")
        return {"message": "Support ticket updated successfully", "data": result}
    except Exception as e:
        logger.error(f"[update_support_ticket_route] Failed to update ticket {ticket_id}: {e}")
        raise

@router.delete("/{ticket_id}", response_model=dict)
async def delete_support_ticket_route(ticket_id: str):
    logger.debug(f"[delete_support_ticket_route] Called with ticket_id={ticket_id}")
    try:
        await delete_support_ticket(ticket_id)
        logger.info(f"[delete_support_ticket_route] Ticket deleted for id={ticket_id}")
        return {"message": "Support ticket deleted successfully"}
    except Exception as e:
        logger.error(f"[delete_support_ticket_route] Failed to delete ticket {ticket_id}: {e}")
        raise

@router.get("/status/{status}", response_model=dict)
async def get_tickets_by_status_route(status: str):
    logger.debug(f"[get_tickets_by_status_route] Called with status={status}")
    try:
        result = await get_tickets_by_status(status)
        logger.info(f"[get_tickets_by_status_route] Fetched {len(result) if result else 0} tickets with status={status}")
        return {
            "message": f"Support tickets with status '{status}' fetched successfully",
            "data": result
        }
    except Exception as e:
        logger.error(f"[get_tickets_by_status_route] Failed to fetch tickets with status {status}: {e}")
        raise
