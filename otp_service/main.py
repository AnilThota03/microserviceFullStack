from fastapi import FastAPI
from otp_service.routers import otp

app = FastAPI(title="OTP Service")
app.include_router(otp.router)

@app.get("/")
def root():
    return {"message": "OTP Service running"}
