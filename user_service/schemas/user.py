from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    email: Optional[str] = Field(None, alias="email")
    contact: Optional[str] = Field(None, alias="contact")

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    contact: Optional[str] = Field(None, alias="contact")
    email: Optional[str] = Field(None, alias="email")

class UserOut(UserBase):
    id: str = Field(..., alias="_id")
    role: Optional[str]
    picture: Optional[str]
    is_verified: Optional[bool] = Field(False, alias="isVerified")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        validate_by_name = True
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
        }

class UserLogin(BaseModel):
    email: EmailStr
    password: str
