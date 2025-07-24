# In translation_document_service/main.py

import sys
import os

# ✅ THIS BLOCK MUST BE FIRST
# This adds the parent directory (microBackend) to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI
from user_service.routers import user

app = FastAPI(title="User Service")
app.include_router(user.router)

@app.get("/")
def root():
    return {"message": "User Service running"}
