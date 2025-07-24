from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class AnnouncementBase(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class AnnouncementCreate(AnnouncementBase):
    pass

class AnnouncementOut(AnnouncementBase):
    id: str = Field(..., alias="_id")
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        validate_by_name = True
        from_attributes = True

class AnnouncementEmail(BaseModel):
    email: Optional[EmailStr] = None
