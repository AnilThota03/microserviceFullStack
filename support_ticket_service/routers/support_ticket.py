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

router = APIRouter(
    prefix="/api/support-ticket",
    tags=["Support Tickets"]
)

@router.post("/", response_model=dict)
async def create_support_ticket_route(ticket: SupportTicketCreate):
    result = await create_support_ticket(ticket)
    return {"message": "Support ticket created successfully", "data": result}

@router.get("/", response_model=dict)
async def get_support_tickets_route():
    result = await get_support_tickets()
    return {"message": "Support tickets fetched successfully", "data": result}

@router.get("/{ticket_id}", response_model=dict)
async def get_support_ticket_by_id_route(ticket_id: str):
    result = await get_support_ticket_by_id(ticket_id)
    return {"message": "Support ticket fetched successfully", "data": result}

@router.patch("/{ticket_id}", response_model=dict)
async def update_support_ticket_route(ticket_id: str, body: SupportTicketUpdate):
    result = await update_support_ticket(ticket_id, body)
    return {"message": "Support ticket updated successfully", "data": result}

@router.delete("/{ticket_id}", response_model=dict)
async def delete_support_ticket_route(ticket_id: str):
    await delete_support_ticket(ticket_id)
    return {"message": "Support ticket deleted successfully"}

@router.get("/status/{status}", response_model=dict)
async def get_tickets_by_status_route(status: str):
    result = await get_tickets_by_status(status)
    return {
        "message": f"Support tickets with status '{status}' fetched successfully",
        "data": result
    }
