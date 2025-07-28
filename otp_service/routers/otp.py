

import logging
from fastapi import APIRouter, HTTPException, status, Body
from ..schemas.otp import OtpRequest, OtpVerify
from ..services.otp import create_temp_user, verify_otp_and_register, resend_otp, mail_sender_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/otp",
    tags=["OTP Verification"]
)

@router.post("/test-mail", response_model=dict)
async def test_mail_route(
    to: str = Body(...),
    subject: str = Body(default="Test Email from OTP Service"),
    text: str = Body(default="This is a test email from the OTP microservice.")
):
    logger.debug(f"[test_mail_route] Called with to={to}, subject={subject}")
    try:
        result = await mail_sender_service(to=to, subject=subject, text=text)
        logger.info(f"[test_mail_route] Mail sent successfully to {to}")
        logger.debug(f"[test_mail_route] Result: {result}")
        return {"message": "Mail sent successfully.", "result": result}
    except Exception as e:
        logger.error(f"[test_mail_route] Mail sending failed for {to}: {e}")
        raise HTTPException(status_code=500, detail=f"Mail sending failed: {e}")


@router.post("/send", response_model=dict)
async def send_otp_route(request: OtpRequest):
    logger.debug(f"[send_otp_route] Called with email={request.email}")
    try:
        await create_temp_user(request.model_dump())
        logger.info(f"[send_otp_route] OTP sent to {request.email}")
        return {"message": "OTP sent to your email."}
    except Exception as e:
        logger.error(f"[send_otp_route] Failed to send OTP to {request.email}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {e}")

@router.post("/verify-otp", response_model=dict)
async def verify_otp_route(request: OtpVerify):
    logger.debug(f"[verify_otp_route] Called with email={request.email}, otp={request.otp}")
    try:
        success = await verify_otp_and_register(request.email, request.otp)
        if not success:
            logger.warning(f"[verify_otp_route] Invalid or expired OTP for {request.email}")
            raise HTTPException(status_code=400, detail="Invalid or expired OTP.")
        logger.info(f"[verify_otp_route] OTP verified and user registered for {request.email}")
        return {"message": "User verified and registered successfully."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[verify_otp_route] Unexpected error for {request.email}: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify OTP.")

@router.post("/resend-otp", response_model=dict)
async def resend_otp_route(request: OtpRequest):
    logger.debug(f"[resend_otp_route] Called with email={request.email}")
    try:
        success = await resend_otp(request.email)
        if not success:
            logger.warning(f"[resend_otp_route] No pending signup found for {request.email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No pending signup found for this email"
            )
        logger.info(f"[resend_otp_route] New OTP sent to {request.email}")
        return {"message": "New OTP sent to your email"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[resend_otp_route] Unexpected error for {request.email}: {e}")
        raise HTTPException(status_code=500, detail="Failed to resend OTP.")
