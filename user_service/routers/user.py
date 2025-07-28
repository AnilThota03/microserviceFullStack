
# All imports at the top
import httpx
import logging
import os
from typing import Optional
from fastapi import (APIRouter, Body, Depends, File, Form, HTTPException, Path, UploadFile, status)
from user_service.schemas.user import UserCreate, UserLogin, UserUpdate
from user_service.services.user import change_password, create_user, delete_user, email_verification_for_forgot_password, get_user_by_id    , reset_password, update_user, admin_login
# If you have authentication dependencies, import or stub them here
# from ..dependencies.auth import get_current_user, require_admin

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/user/api",
    tags=["User"]
)

# --- OTP-based Signup and Verification Routes ---
# Removed duplicate signup_email_route to resolve function name conflict.

@router.post("/verify-otp", response_model=dict)
async def verify_otp_route(email: str = Body(...), otp: str = Body(...)):
    logger.debug(f"[verify_otp_route] Called with email={email}, otp={otp}")
    otp_service_url = os.getenv("OTP_SERVICE_URL", "http://localhost:8005/api/otp/verify-otp")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(otp_service_url, json={"email": email, "otp": otp})
            response.raise_for_status()
            data = response.json()
        logger.info(f"[verify_otp_route] OTP verification successful for email={email}")
        logger.debug(f"[verify_otp_route] Success: {data}")
        return {"message": data.get("message", "User verified and registered successfully.")}
    except httpx.HTTPStatusError as e:
        logger.warning(f"[verify_otp_route] OTP verification failed for email={email}: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"OTP verification failed: {e.response.text}")
    except Exception as e:
        logger.error(f"[verify_otp_route] Unexpected error for email={email}: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify OTP.")

@router.post("/resend-otp", response_model=dict)
async def resend_otp_route(email: str = Body(...)):
    logger.debug(f"[resend_otp_route] Called with email={email}")
    otp_service_url = os.getenv("OTP_SERVICE_URL", "http://localhost:8005/api/otp/resend-otp")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(otp_service_url, json={"email": email})
            response.raise_for_status()
            data = response.json()
        logger.info(f"[resend_otp_route] OTP resent successfully for email={email}")
        logger.debug(f"[resend_otp_route] Success: {data}")
        return {"message": data.get("message", "New OTP sent to your email")}
    except httpx.HTTPStatusError as e:
        logger.warning(f"[resend_otp_route] Resend OTP failed for email={email}: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Resend OTP failed: {e.response.text}")
    except Exception as e:
        logger.error(f"[resend_otp_route] Unexpected error for email={email}: {e}")
        raise HTTPException(status_code=500, detail="Failed to resend OTP.")


@router.post("/signup-email", response_model=dict)
async def signup_email_route(user: UserCreate):
    logger.debug(f"[signup_email_route] Called with user={user}")
    if not user.email:
        logger.error("[signup_email_route] Signup-email failed: Email is required.")
        raise HTTPException(status_code=400, detail="Email is required.")
    otp_service_url = os.getenv("OTP_SERVICE_URL", "http://localhost:8005/api/otp/send")
    # Send all user registration fields to OTP service for temp user creation
    otp_payload = user.model_dump(by_alias=True)
    print(otp_payload)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(otp_service_url, json=otp_payload)
            response.raise_for_status()
            data = response.json()
        logger.info(f"[signup_email_route] OTP sent successfully to {user.email}")
        logger.debug(f"[signup_email_route] OTP sent: {data}")
        return {"message": data.get("message", "OTP sent to your email. Please verify to complete registration.")}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 409:
            logger.warning(f"[signup_email_route] Signup attempt for existing user: {user.email}")
            raise HTTPException(status_code=409, detail="Email already registered. Please login or use forgot password.")
        logger.error(f"[signup_email_route] Error for {user.email}: {e.response.text}")
        raise HTTPException(status_code=500, detail=f"OTP service error: {e.response.text} {e} {e.response}")
    except Exception as e:
        logger.error(f"[signup_email_route] Unexpected error for {user.email}: {e}")
        raise HTTPException(status_code=500, detail="Failed to send OTP for signup.")

@router.get("/user/{id}", response_model=dict)
async def get_user_route(id: str):
    logger.debug(f"[get_user_route] Called with id={id}")
    result = await get_user_by_id(id)
    logger.debug(f"[get_user_route] Result: {result}")
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
    logger.debug(f"[update_user_route] Called with id={id}, file={'Yes' if file else 'No'}")
    update_fields = {}
    if firstName is not None and firstName.strip() != "":
        update_fields["firstName"] = firstName.strip()
    if lastName is not None and lastName.strip() != "":
        update_fields["lastName"] = lastName.strip()
    if contact is not None and contact.strip() != "":
        update_fields["contact"] = contact.strip()
    if email is not None and email.strip() != "":
        update_fields["email"] = email.strip()
    user_data = UserUpdate(**update_fields)
    result = await update_user(id, user_data, file if file and file.filename else None)
    logger.debug(f"[update_user_route] Result: {result}")
    return {"message": "User updated successfully", "data": result}

@router.delete("/{id}", response_model=dict)
async def delete_user_route(id: str = Path(..., title="The ID of the user to delete")):
    logger.debug(f"[delete_user_route] Called with id={id}")
    result = await delete_user(id)
    logger.debug(f"[delete_user_route] Result: {result}")
    return result

@router.delete("/admin/{id}", response_model=dict)
async def delete_user_by_admin_route(id: str):
    logger.debug(f"[delete_user_by_admin_route] Called with id={id}")
    await delete_user(id)
    logger.debug(f"[delete_user_by_admin_route] User deleted")
    return {"message": "User deleted successfully"}

@router.post("/user/login", response_model=dict)
async def login_route(user: UserLogin):
    logger.debug(f"[login_route] Called with user={user}")
    from user_service.services.user import login_user
    result = await login_user(user)
    logger.debug(f"[login_route] Result: {result}")
    return result

@router.post("/userLoginWithGoogle", response_model=dict)
async def login_with_google_route(data: dict = Body(...)):
    logger.debug(f"[login_with_google_route] Called with data={data}")
    # login_with_google is not implemented in services, so raise error or comment out
    raise NotImplementedError("login_with_google is not implemented.")
    # result = await login_with_google(data["data"])
    # logger.debug(f"[login_with_google_route] Result: {result}")
    # return result

@router.post("/admin/login", response_model=dict)
async def admin_login_route(email: str = Body(...), password: str = Body(...)):
    logger.debug(f"[admin_login_route] Called with email={email}")
    result = await admin_login(email, password)
    logger.debug(f"[admin_login_route] Result: {result}")
    return result

@router.post("/forgot-password", response_model=dict)
async def forgot_password_route(email: str = Body(...)):
    logger.debug(f"[forgot_password_route] Called with email={email}")
    result = await email_verification_for_forgot_password(email)
    logger.debug(f"[forgot_password_route] Result: {result}")
    return result

@router.post("/reset-password/{user_id}", response_model=dict)
async def reset_password_route(user_id: str, new_password: str = Body(...)):
    logger.debug(f"[reset_password_route] Called with user_id={user_id}")
    result = await reset_password(user_id, new_password)
    logger.debug(f"[reset_password_route] Result: {result}")
    return result

@router.post("/change-password/{user_id}", response_model=dict)
async def change_password_route(
    user_id: str,
    body: dict = Body(...)
):
    logger.debug(f"[change_password_route] Called with user_id={user_id}")
    current_password = body.get("currentPassword")
    new_password = body.get("newPassword")
    confirm_password = body.get("confirmPassword")
    if not all([current_password, new_password, confirm_password]):
        logger.error(f"[change_password_route] Missing fields for user {user_id}")
        raise HTTPException(status_code=400, detail="All fields are required")
    if not isinstance(current_password, str) or not isinstance(new_password, str):
        logger.error(f"[change_password_route] Invalid password types for user {user_id}")
        raise HTTPException(status_code=400, detail="Invalid password format.")
    if new_password != confirm_password:
        logger.error(f"[change_password_route] Passwords do not match for user {user_id}")
        raise HTTPException(status_code=400, detail="Passwords do not match")
    result = await change_password(user_id, str(current_password), str(new_password))
    logger.debug(f"[change_password_route] Result: {result}")
    return result
