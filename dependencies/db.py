# db.py for user_service dependencies
from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config
import os

MONGO_URL = config('MONGODB_URL', default='mongodb://localhost:27017/PDIT')

# Add this line to check
print(f"Attempting to connect with URL: {MONGO_URL}") 

client = AsyncIOMotorClient(MONGO_URL)
db_name = MONGO_URL.rsplit("/", 1)[-1].split("?", 1)[0]
db = client[db_name]