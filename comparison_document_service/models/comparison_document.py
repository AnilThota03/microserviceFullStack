from microserviceFullStack.dependencies.db import db

def get_comparison_document_collection():
    return db["comparison_documents"]
