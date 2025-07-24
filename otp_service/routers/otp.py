from fastapi import APIRouter, HTTPException, status
from ..schemas.otp import OtpRequest, OtpVerify
from ..services.otp import create_temp_user, verify_otp_and_register, resend_otp

router = APIRouter(
    prefix="/api/otp",
    tags=["OTP Verification"]
)

@router.post("/send", response_model=dict)
async def send_otp_route(request: OtpRequest):
    await create_temp_user(request.model_dump())
    return {"message": "OTP sent to your email."}

@router.post("/verify-otp", response_model=dict)
async def verify_otp_route(request: OtpVerify):
    success = await verify_otp_and_register(request.email, request.otp)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")
    return {"message": "User verified and registered successfully."}

@router.post("/resend-otp", response_model=dict)
async def resend_otp_route(request: OtpRequest):
    success = await resend_otp(request.email)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending signup found for this email"
        )
    return {"message": "New OTP sent to your email"}
