from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime

class OtpRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")


class OtpVerify(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    otp: str = Field(..., min_length=4, max_length=10, description="The OTP sent to the user's email")

class TempUser(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    contact: Optional[str] = None
    picture: Optional[str] = None
    role: str = "user"
    # is_verified: bool = Field(False, alias="isVerified")
    # created_at: Optional[datetime] = Field(None, alias="createdAt")
    # updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    # expires_at: Optional[datetime] = Field(None, alias="expiresAt")

    model_config = ConfigDict(validate_by_name=True, from_attributes=True)

class Verification(BaseModel):
    email: EmailStr
    otp: str
    created_at: datetime = Field(..., alias="createdAt")
    expires_at: datetime = Field(..., alias="expiresAt")

    model_config = ConfigDict(validate_by_name=True, from_attributes=True)
