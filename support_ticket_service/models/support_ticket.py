from microserviceFullStack.dependencies.db import db

def get_support_ticket_collection():
    return db["supporttickets"]
