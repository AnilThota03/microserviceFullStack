
from dependencies.db import db

def get_temp_user_collection():
    return db["temp_users"]


def get_verification_collection():
    return db["verifications"]
