from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class SupportTicketBase(BaseModel):
    email: Optional[EmailStr] = None
    message: Optional[str] = None
    status: Optional[str] = "open"

class SupportTicketCreate(SupportTicketBase):
    pass

class SupportTicketUpdate(BaseModel):
    status: Optional[str]

class SupportTicketOut(SupportTicketBase):
    id: str = Field(..., alias="_id")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        validate_by_name = True
        from_attributes = True
