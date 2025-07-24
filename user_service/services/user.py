from user_service.models.user import get_user_collection
from user_service.schemas.user import UserCreate, UserUpdate, UserOut, UserLogin
from passlib.context import CryptContext
from jose import jwt
# from ...config import settings  # Adjust import as needed
from bson import ObjectId
from fastapi import HTTPException, UploadFile
from datetime import datetime, timedelta
# from ..models.otp import get_verification_collection
# from ..services.mail_sender import mail_sender_service
# from ..services.azure_blob import upload_to_blob_storage, delete_blob_from_url
import os
from typing import Optional
from decouple import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        k: v for k, v in user.dict(exclude_unset=True, exclude_none=True).items()
        if k != "password"
    }
    update_data["updatedAt"] = datetime.utcnow()
    # Blob upload and picture logic omitted for brevity
    updated = await users.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": update_data},
        return_document=True
    )
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    updated["_id"] = str(updated["_id"])
    return UserOut(**updated)

async def delete_user(id: str):
    users = get_user_collection()
    result = await users.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

async def login_user(user: UserLogin):
    users = get_user_collection()
    db_user = await users.find_one({"email": user.email})
    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    db_user["_id"] = str(db_user["_id"])
    # token = jwt.encode({"user_id": db_user["_id"]}, settings.JWT_SECRET, algorithm="HS256")
    return {"user": db_user, "jwt": "token", "message": "Login successful", "status": 200}

async def login_with_google(data):
    print("[SERVICE] login_with_google called")

    print(" ❤️❤️",data)
    users = get_user_collection()
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required for Google login")

    user = await users.find_one({"email": email})
    if not user:
        user_doc = {
            "email": email,
            "firstName": data.get("given_name"),
            "lastName": data.get("family_name"),
            "picture":  "https://res.cloudinary.com/dizbakfcc/image/upload/v1751972291/profilePlaceholder_lcrcd0.png",
            "isVerified": True,
            "role": "user",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "contact":"0000000000"
        }
        result = await users.insert_one(user_doc)
        user = await users.find_one({"_id": result.inserted_id})

    user["_id"] = str(user["_id"])
    token = jwt.encode({"user_id": user["_id"]}, config("JWT_SECRET"), algorithm="HS256")
    return {
    "user": UserOut(**user).dict(by_alias=True),
    "jwt": token,
    "message": "Google login successful"
    }

async def admin_login(email: str, password: str):
    if email == "adminpdit26@gmail.com" and password == "Pdit@26":
        # token = jwt.encode({"role": "admin"}, settings.JWT_SECRET, algorithm="HS256")
        return {"jwt": "token", "role": "admin", "message": "Admin login successful"}
    raise HTTPException(status_code=401, detail="Invalid admin credentials")

async def email_verification_for_forgot_password(email: str):
    users = get_user_collection()
    if not await users.find_one({"email": email}):
        raise HTTPException(status_code=404, detail="User not found")
    # Email sending logic omitted for brevity
    return {"message": "Verification email sent"}

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
