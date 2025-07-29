
from microserviceFullStack.dependencies.db import db


def get_document_collection():
    """
    Returns the MongoDB collection for translation documents.
    Handles missing DB connection gracefully.
    """
    if db is None:
        raise RuntimeError("Database connection is not initialized.")
    return db["translation_documents"]
