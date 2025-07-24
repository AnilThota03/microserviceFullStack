from microBackend.dependencies.db import db

def get_user_collection():
    return db["users"]
