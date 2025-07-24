from microserviceFullStack.dependencies.db import db

def get_admin_reply_collection():
    return db["adminreplies"]
