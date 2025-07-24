# In translation_document_service/main.py

import sys
import os

# ✅ THIS BLOCK MUST BE FIRST
# This adds the parent directory (microBackend) to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Now, other imports will work correctly
from fastapi import FastAPI
from translation_document_service.routers import translation_document

app = FastAPI(title="Translation Document Service")
app.include_router(translation_document.router)

@app.get("/")
def root():
    return {"message": "Translation Document Service running"}