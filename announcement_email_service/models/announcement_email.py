from microserviceFullStack.dependencies.db import db

def get_announcement_email_collection():
    return db["announcementEmails"]
