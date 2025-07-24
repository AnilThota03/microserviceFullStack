from microserviceFullStack.dependencies.db import db

def get_announcement_collection():
    return db["announcements"]
