from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AdminReplyBase(BaseModel):
    ticket_id: Optional[str] = Field(None, alias="ticketId")
    subject: Optional[str]
    body: Optional[str]
    replied_by: Optional[str] = Field("admin", alias="repliedBy")

class AdminReplyCreate(AdminReplyBase):
    pass

class AdminReplyOut(AdminReplyBase):
    id: str = Field(..., alias="_id")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        validate_by_name = True
        from_attributes = True
