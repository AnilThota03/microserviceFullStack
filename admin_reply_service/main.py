from fastapi import FastAPI
from routers import admin_reply

app = FastAPI(title="Admin Reply Service")
app.include_router(admin_reply.router)

@app.get("/")
def root():
    return {"message": "Admin Reply Service running"}
