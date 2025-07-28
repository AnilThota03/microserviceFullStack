
from fastapi import APIRouter, HTTPException, status, Body
from ..schemas.otp import OtpRequest, OtpVerify
from ..services.otp import create_temp_user, verify_otp_and_register, resend_otp, mail_sender_service

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
    try:
        result = await mail_sender_service(to=to, subject=subject, text=text)
        return {"message": "Mail sent successfully.", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mail sending failed: {e}")


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
