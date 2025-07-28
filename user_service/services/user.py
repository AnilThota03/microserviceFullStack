# --- DELETE USER SERVICE ---
async def delete_user(id: str):
    users = get_user_collection()
    result = await users.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
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

# --- LOGIN USER SERVICE ---
async def login_user(user: UserLogin):
    users = get_user_collection()
    db_user = await users.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not pwd_context.verify(user.password, db_user.get("password", "")):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    db_user["_id"] = str(db_user["_id"])
    jwt_secret = os.getenv("JWT_SECRET", "changeme")
    token = jwt.encode({"user_id": db_user["_id"]}, jwt_secret, algorithm="HS256")
    return {"jwt": token, "user": UserOut(**db_user), "message": "Login successful"}

# --- LOGIN WITH GOOGLE SERVICE ---
async def login_with_google(data: dict):
    users = get_user_collection()
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required for Google login")
    user = await users.find_one({"email": email})
    if not user:
        user_doc = {
            "email": email,
            "firstName": data.get("given_name") or data.get("firstName", ""),
            "lastName": data.get("family_name") or data.get("lastName", ""),
            "picture": data.get("picture", "https://res.cloudinary.com/dizbakfcc/image/upload/v1751972291/profilePlaceholder_lcrcd0.png"),
            "isVerified": True,
            "role": "user",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "contact": data.get("contact", "0000000000")
        }
        result = await users.insert_one(user_doc)
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create user with Google login")
        user = await users.find_one({"_id": result.inserted_id})
    if not user:
        raise HTTPException(status_code=500, detail="User not found after Google login")
    user = dict(user)
    user["_id"] = str(user["_id"])
    jwt_secret = os.getenv("JWT_SECRET", "changeme")
    token = jwt.encode({"user_id": user["_id"]}, jwt_secret, algorithm="HS256")
    try:
        user_out = UserOut(**user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"UserOut serialization error: {e}")
    return {"jwt": token, "user": user_out, "message": "Google login successful"}

# Optional: import OTP, mail, and blob logic if available in microservice
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

# Optional: import OTP, mail, and blob logic if available in microservice
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
    if get_verification_collection and mail_sender_service:
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        verification = get_verification_collection()
        await verification.insert_one({
            "email": email,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "used": False
        })
        subject = "PDIT Password Reset Verification"
        text = f"A password reset was requested for your account. This link will expire in 5 minutes."
        await mail_sender_service(to=email, subject=subject, text=text)
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
