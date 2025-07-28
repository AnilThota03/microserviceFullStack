

import random
import string
from datetime import datetime, timedelta
from fastapi import HTTPException
from passlib.context import CryptContext
from otp_service.models.otp import get_temp_user_collection, get_verification_collection
from user_service.models.user import get_user_collection
import os
from decouple import config

# Use the same password context as dependencies
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurable OTP expiry and mail service URL
OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", config("OTP_EXPIRY_MINUTES", default=5)))
MAIL_SERVICE_URL = str(os.getenv("MAIL_SERVICE_URL") or config("MAIL_SERVICE_URL", default="http://localhost:8001/send-mail/"))

# Dependency-style mail sender
from dependencies.mail_service import send_mail as mail_sender_service

async def send_otp(email: str) -> str:
    otp = ''.join(random.choices(string.digits, k=6))
    now = datetime.utcnow()
    verifications = get_verification_collection()
    await verifications.insert_one({
        "email": email,
        "otp": otp,
        "createdAt": now,
        "expiresAt": now + timedelta(minutes=OTP_EXPIRY_MINUTES),
        "used": False
    })
    subject = "Your OTP for PDIT Registration"
    text = f"Your OTP is: {otp}. It will expire in {OTP_EXPIRY_MINUTES} minutes."
    try:
        await mail_sender_service(to=email, subject=subject, text=text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP email: {e}")
    return otp

async def create_temp_user(user_data: dict):
    temp_users = get_temp_user_collection()
    users = get_user_collection()
    now = datetime.utcnow()
    if await users.find_one({"email": user_data["email"]}):
        raise HTTPException(status_code=409, detail="Email already registered")
    existing_temp_user = await temp_users.find_one({"email": user_data["email"]})
    hashed_password = pwd_context.hash(user_data["password"])
    doc = {
        "email": user_data["email"],
        "password": hashed_password,
        "firstName": user_data.get("firstName", ""),
        "lastName": user_data.get("lastName", ""),
        "role": user_data.get("role", "user"),
        "isVerified": False,
        "createdAt": now,
        "updatedAt": now
    }
    if existing_temp_user:
        await temp_users.update_one({"email": user_data["email"]}, {"$set": doc})
    else:
        await temp_users.insert_one(doc)
    await send_otp(user_data["email"])


async def verify_otp_and_register(email: str, otp: str):
    verifications = get_verification_collection()
    temp_users = get_temp_user_collection()
    users = get_user_collection()
    record = await verifications.find_one({"email": email, "otp": otp, "used": False})
    if not record or record["expiresAt"] < datetime.utcnow():
        return False
    temp_user = await temp_users.find_one({"email": email})
    if not temp_user:
        return False
    temp_user["isVerified"] = True
    temp_user["createdAt"] = datetime.utcnow()
    temp_user["updatedAt"] = datetime.utcnow()
    await users.insert_one(temp_user)
    await verifications.delete_one({"_id": record["_id"]})
    await temp_users.delete_one({"_id": temp_user["_id"]})
    return True


async def resend_otp(email: str) -> bool:
    temp_users = get_temp_user_collection()
    verifications = get_verification_collection()
    temp_user = await temp_users.find_one({"email": email})
    if not temp_user:
        return False
    await verifications.delete_many({"email": email, "used": False})
    await send_otp(email)
    return True
