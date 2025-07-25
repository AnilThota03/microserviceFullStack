import logging
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

@router.post("/signup-email", response_model=dict)
async def signup_email_route(user: UserCreate):
    logger.info(f"Received email signup request for: {user.email}")
    # If you have a temp user creation service, call it here
    # await create_temp_user(user.model_dump(by_alias=True))
    return {"message": "OTP sent to your email. Please verify to complete registration."}

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
    user_data = UserUpdate(
        firstName=firstName,
        lastName=lastName,
        contact=contact,
        email=email
    )
    result = await update_user(id, user_data, file)
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
    if new_password != confirm_password:
        logger.error(f"Change password failed for user {user_id}: Passwords do not match.")
        raise HTTPException(status_code=400, detail="Passwords do not match")
    return await change_password(user_id, current_password, new_password)
