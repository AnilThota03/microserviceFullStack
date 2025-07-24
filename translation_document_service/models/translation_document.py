from microBackend.dependencies.db import db

def get_document_collection():
    # Replace with actual db connection logic
    return db["translation_documents"]
