from fastapi import FastAPI
from routers import announcement_email

app = FastAPI(title="Announcement Email Service")
app.include_router(announcement_email.router)

@app.get("/")
def root():
    return {"message": "Announcement Email Service running"}
