# In translation_document_service/main.py

import sys
import os

# ✅ THIS BLOCK MUST BE FIRST
# This adds the parent directory (microBackend) to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


from fastapi import FastAPI
from comparison_document_service.routers import comparison_document

app = FastAPI(title="Comparison Document Service")
app.include_router(comparison_document.router)

@app.get("/")
def root():
    return {"message": "Comparison Document Service running"}
