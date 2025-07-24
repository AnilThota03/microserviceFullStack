def serialize_ticket(ticket):
    ticket["id"] = str(ticket["_id"])
    ticket.pop("_id", None)
    from ..schemas.support_ticket import SupportTicketOut
    return SupportTicketOut(**ticket)

from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime
from ..models.support_ticket import get_support_ticket_collection
from ..schemas.support_ticket import SupportTicketCreate, SupportTicketUpdate, SupportTicketOut
from ..services.mail_sender import mail_sender_service

async def create_support_ticket(ticket: SupportTicketCreate):
    tickets = get_support_ticket_collection()
    ticket_dict = ticket.dict()
    ticket_dict["created_at"] = datetime.utcnow()
    ticket_dict["updated_at"] = datetime.utcnow()
    result = await tickets.insert_one(ticket_dict)
    ticket_dict["id"] = str(result.inserted_id)
    await mail_sender_service(
        to=ticket.email,
        subject="Support Ticket Received",
        text="Thank you for reaching out to PDIT Support. Your request has been received and our team will get back to you shortly.",
        html=f"<p>Thank you for reaching out to PDIT Support. Your request has been received and our team will get back to you shortly.</p>"
    )
    ticket_dict["_id"] = str(result.inserted_id)
    return SupportTicketOut(**ticket_dict)

async def get_support_tickets():
    tickets = get_support_ticket_collection()
    result = []
    async for ticket in tickets.find({}):
        result.append(serialize_ticket(ticket))
    return result

async def get_support_ticket_by_id(ticket_id: str):
    tickets = get_support_ticket_collection()
    ticket = await tickets.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")
    return serialize_ticket(ticket)

async def update_support_ticket(ticket_id: str, ticket: SupportTicketUpdate):
    tickets = get_support_ticket_collection()
    update_data = {k: v for k, v in ticket.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    updated = await tickets.find_one_and_update(
        {"_id": ObjectId(ticket_id)},
        {"$set": update_data},
        return_document=True
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Support ticket not found")
    return serialize_ticket(updated)

async def delete_support_ticket(ticket_id: str):
    tickets = get_support_ticket_collection()
    result = await tickets.delete_one({"_id": ObjectId(ticket_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Support ticket not found")
    return {"message": "Support ticket deleted successfully"}

async def get_tickets_by_status(status: str):
    tickets = get_support_ticket_collection()
    result = []
    async for ticket in tickets.find({"status": status}):
        result.append(serialize_ticket(ticket))
    return result
