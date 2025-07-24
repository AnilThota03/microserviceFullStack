from fastapi import FastAPI
from routers import announcement

app = FastAPI(title="Announcement Service")
app.include_router(announcement.router)

@app.get("/")
def root():
    return {"message": "Announcement Service running"}
