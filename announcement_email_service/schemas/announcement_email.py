from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

class AnnouncementEmailIn(BaseModel):
    email: EmailStr
    user_id: Optional[str] = None

class AnnouncementEmailOut(BaseModel):
    email: EmailStr
    user_id: Optional[str] = None
    subscribed: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[str] = Field(None, alias="_id")

    class Config:
        validate_by_name = True
        from_attributes = True

class AnnouncementEmailModel(BaseModel):
    email: EmailStr = Field(..., description="User email")
    user_id: Optional[str] = Field(default=None, alias="userId")
    subscribed: bool = Field(default=False)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, alias="updatedAt")

    class Config:
        validate_by_name = True
        from_attributes = True
        json_encoders = {ObjectId: str}
