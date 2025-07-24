# In translation_document_service/main.py

import sys
import os

# ✅ THIS BLOCK MUST BE FIRST
# This adds the parent directory (microBackend) to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI
from project_service.routers import project

app = FastAPI(title="Project Service")
app.include_router(project.router)

@app.get("/")
def root():
    return {"message": "Project Service running"}
