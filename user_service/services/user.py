# --- LOGIN USER SERVICE ---
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException
from user_service.models.user import get_user_collection
from user_service.schemas.user import UserLogin
import os
class Settings:
    JWT_SECRET = os.getenv("JWT_SECRET", "changeme")
settings = Settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def login_user(user: UserLogin):
    users = get_user_collection()
    db_user = await users.find_one({"email": user.email})
    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    db_user["_id"] = str(db_user["_id"])
    token = jwt.encode({"user_id": db_user["_id"]}, settings.JWT_SECRET, algorithm="HS256")
    return {"user": db_user, "jwt": token, "message": "Login successful", "status": 200}

# --- CLEANED IMPORTS ---
from user_service.models.user import get_user_collection
from user_service.schemas.user import UserCreate, UserUpdate, UserOut, UserLogin
from passlib.context import CryptContext
from jose import jwt
from bson import ObjectId
from fastapi import HTTPException, UploadFile
from datetime import datetime, timedelta
import os
from typing import Optional
from decouple import config
import httpx
try:
    from user_service.models.otp import get_verification_collection
except ImportError:
    get_verification_collection = None
from dependencies.mail_service import send_mail as mail_sender_service
try:
    from dependencies.azure_blob_service import upload_to_blob_storage, delete_blob_from_url
except ImportError:
    upload_to_blob_storage = None
    delete_blob_from_url = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- DELETE USER SERVICE ---
async def delete_user(id: str):
    users = get_user_collection()
    result = await users.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

async def create_user(user: UserCreate):
    users = get_user_collection()
    if await users.find_one({"email": user.email}):
        raise HTTPException(status_code=409, detail="Email already exists")
    user_dict = user.dict()
    user_dict.update({
        "password": pwd_context.hash(user.password),
        "isVerified": False,
        "role": "user",
        "contact": user.contact,
        "picture": "https://res.cloudinary.com/dizbakfcc/image/upload/v1751972291/profilePlaceholder_lcrcd0.png",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    })
    result = await users.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)
    return UserOut(**user_dict)

async def get_user_by_id(id: str):
    users = get_user_collection()
    user = await users.find_one({"_id": ObjectId(id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["_id"] = str(user["_id"])
    user.setdefault("picture", "https://res.cloudinary.com/dizbakfcc/image/upload/v1751972291/profilePlaceholder_lcrcd0.png")
    return UserOut(**user)

async def update_user(id: str, user: UserUpdate, file: Optional[UploadFile] = None):
    users = get_user_collection()
    update_data = {
        k: v for k, v in user.dict(exclude_unset=True, exclude_none=True, by_alias=True).items()
        if k != "password"
    }
    update_data["updatedAt"] = datetime.utcnow()

    # Efficient blob storage logic: only update picture if a new file is provided
    if file and file.filename and upload_to_blob_storage:
        try:
            ext = os.path.splitext(file.filename)[-1]
            # Use firstName from update_data, fallback to DB value, fallback to 'profile'
            first_name = update_data.get("firstName")
            if not first_name:
                existing_user = await users.find_one({"_id": ObjectId(id)})
                first_name = existing_user.get("firstName") if existing_user else "profile"
            custom_blob_name = f"profiles/{str(first_name).strip().lower()}{ext}"

            # Delete old picture if exists
            existing_user = await users.find_one({"_id": ObjectId(id)})
            old_picture_url = existing_user.get("picture") if existing_user else None
            if old_picture_url and delete_blob_from_url:
                try:
                    await delete_blob_from_url(old_picture_url)
                except Exception:
                    pass

            # Upload new picture
            blob_url = await upload_to_blob_storage(
                "pdit",
                file,
                custom_blob_name
            )
            update_data["picture"] = blob_url
        except Exception as e:
            raise HTTPException(status_code=500, detail="Image upload failed")

    # If no file, do not touch the picture field; previous image remains
    updated = await users.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": update_data},
        return_document=True
    )
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    updated["_id"] = str(updated["_id"])
    return UserOut(**updated)


async def admin_login(email: str, password: str):
    if email == "adminpdit26@gmail.com" and password == "Pdit@26":
        jwt_secret = os.getenv("JWT_SECRET", "changeme")
        token = jwt.encode({"role": "admin"}, jwt_secret, algorithm="HS256")
        return {"jwt": token, "role": "admin", "message": "Admin login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

async def email_verification_for_forgot_password(email: str):
    users = get_user_collection()
    if not await users.find_one({"email": email}):
        raise HTTPException(status_code=404, detail="User not found")
    # Call OTP microservice to send verification email
    otp_service_url = os.getenv("OTP_SERVICE_URL", "http://localhost:8005/api/otp/send")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(otp_service_url, json={"email": email})
            response.raise_for_status()
            data = response.json()
        return {"message": data.get("message", "Verification email sent")}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"OTP service error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send verification email: {e}")

async def reset_password(user_id: str, new_password: str):
    users = get_user_collection()
    if not await users.find_one({"_id": ObjectId(user_id)}):
        raise HTTPException(status_code=404, detail="User not found")
    hashed = pwd_context.hash(new_password)
    await users.update_one({"_id": ObjectId(user_id)}, {"$set": {"password": hashed, "updated_at": datetime.utcnow()}})
    return {"message": "Password reset successful"}

async def change_password(user_id: str, current_password: str, new_password: str):
    users = get_user_collection()
    user = await users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not pwd_context.verify(current_password, user.get("password", "")):
        raise HTTPException(status_code=401, detail="Wrong password")
    hashed_new_password = pwd_context.hash(new_password)
    await users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password": hashed_new_password, "updatedAt": datetime.utcnow()}}
    )
    return {"message": "Password changed successfully"}
