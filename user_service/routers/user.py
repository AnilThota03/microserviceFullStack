import logging
import os
from typing import Optional
from fastapi import (APIRouter, Body, Depends, File, Form, HTTPException, Path, UploadFile, status)
from user_service.schemas.user import UserCreate, UserLogin, UserUpdate
from user_service.services.user import (change_password, create_user, delete_user, email_verification_for_forgot_password, get_user_by_id, login_user, login_with_google, reset_password, update_user, admin_login)
# If you have authentication dependencies, import or stub them here
# from ..dependencies.auth import get_current_user, require_admin

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/user/api",
    tags=["User"]
)

@router.post("/", response_model=dict)
async def create_user_route(user: UserCreate):
    logger.info(f"Attempting to create a new user with email: {user.email}")
    result = await create_user(user)
    logger.info(f"Successfully created user: {user.email}")
    return {"message": "User created successfully", "data": result}


import httpx

@router.post("/signup-email", response_model=dict)
async def signup_email_route(user: UserCreate):
    """
    Handles user signup by email. Calls OTP microservice to create temp user and send OTP for verification.
    """
    logger.info(f"Received email signup request for: {user.email}")
    if not user.email:
        logger.error("Signup-email failed: Email is required.")
        raise HTTPException(status_code=400, detail="Email is required.")
    # Call OTP microservice to create temp user and send OTP
    otp_service_url = os.getenv("OTP_SERVICE_URL", "http://localhost:8002/api/otp/send")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(otp_service_url, json=user.model_dump(by_alias=True))
            response.raise_for_status()
            data = response.json()
        logger.info(f"OTP sent to new user email: {user.email}")
        return {"message": data.get("message", "OTP sent to your email. Please verify to complete registration.")}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 409:
            logger.warning(f"Signup attempt for existing user: {user.email}")
            raise HTTPException(status_code=409, detail="Email already registered. Please login or use forgot password.")
        logger.error(f"Error during signup-email: {e.response.text}")
        raise HTTPException(status_code=500, detail=f"OTP service error: {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error during signup-email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send OTP for signup.")

@router.get("/user/{id}", response_model=dict)
async def get_user_route(id: str):
    logger.info(f"Fetching user with ID: {id}")
    result = await get_user_by_id(id)
    return {"message": "User fetched successfully", "data": result}

@router.put("/user/{id}", response_model=dict)
async def update_user_route(
    id: str,
    firstName: Optional[str] = Form(None),
    lastName: Optional[str] = Form(None),
    contact: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    email: Optional[str] = Form(None)
):
    logger.info(f"Updating user with ID: {id}. File included: {'Yes' if file else 'No'}")
    # Only update fields that are not None and not blank/empty string
    update_fields = {}
    if firstName is not None and firstName.strip() != "":
        update_fields["firstName"] = firstName.strip()
    if lastName is not None and lastName.strip() != "":
        update_fields["lastName"] = lastName.strip()
    if contact is not None and contact.strip() != "":
        update_fields["contact"] = contact.strip()
    if email is not None and email.strip() != "":
        update_fields["email"] = email.strip()

    # Build UserUpdate with only valid fields
    user_data = UserUpdate(**update_fields)

    # Only update picture if a file is provided; if not, previous image remains unchanged
    result = await update_user(id, user_data, file if file and file.filename else None)
    logger.info(f"Successfully updated user: {id}")
    return {"message": "User updated successfully", "data": result}

@router.delete("/{id}", response_model=dict)
async def delete_user_route(id: str = Path(..., title="The ID of the user to delete")):
    logger.info(f"Attempting to delete user with ID: {id}")
    result = await delete_user(id)
    logger.info(f"Successfully deleted user: {id}")
    return result

@router.delete("/admin/{id}", response_model=dict)
async def delete_user_by_admin_route(id: str):
    logger.warning(f"Admin is deleting user with ID: {id}")
    await delete_user(id)
    logger.info(f"Admin successfully deleted user: {id}")
    return {"message": "User deleted successfully"}

@router.post("/user/login", response_model=dict)
async def login_route(user: UserLogin):
    logger.info(f"Login attempt for user: {user.email}")
    result = await login_user(user)
    return result

@router.post("/userLoginWithGoogle", response_model=dict)
async def login_with_google_route(data: dict = Body(...)):
    logger.info(f"Received request to login with Google.")
    result = await login_with_google(data["data"])
    logger.info(f"Login successful with Google for user: {result.get('data', {}).get('email')}")
    return result

@router.post("/admin/login", response_model=dict)
async def admin_login_route(email: str = Body(...), password: str = Body(...)):
    logger.warning(f"Admin login attempt for: {email}")
    result = await admin_login(email, password)
    return result

@router.post("/forgot-password", response_model=dict)
async def forgot_password_route(email: str = Body(...)):
    logger.info(f"Forgot password request for email: {email}")
    result = await email_verification_for_forgot_password(email)
    return result

@router.post("/reset-password/{user_id}", response_model=dict)
async def reset_password_route(user_id: str, new_password: str = Body(...)):
    logger.info(f"Password reset request for user ID: {user_id}")
    result = await reset_password(user_id, new_password)
    return result

@router.post("/change-password/{user_id}", response_model=dict)
async def change_password_route(
    user_id: str,
    body: dict = Body(...)
):
    logger.info(f"Change password request for user ID: {user_id}")
    current_password = body.get("currentPassword")
    new_password = body.get("newPassword")
    confirm_password = body.get("confirmPassword")
    if not all([current_password, new_password, confirm_password]):
        logger.error(f"Change password failed for user {user_id}: Missing fields.")
        raise HTTPException(status_code=400, detail="All fields are required")
    if not isinstance(current_password, str) or not isinstance(new_password, str):
        logger.error(f"Change password failed for user {user_id}: Invalid password types.")
        raise HTTPException(status_code=400, detail="Invalid password format.")
    if new_password != confirm_password:
        logger.error(f"Change password failed for user {user_id}: Passwords do not match.")
        raise HTTPException(status_code=400, detail="Passwords do not match")
    return await change_password(user_id, str(current_password), str(new_password))
