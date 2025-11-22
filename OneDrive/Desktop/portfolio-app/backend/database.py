from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os

# Use container name in Docker, localhost for local development
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://admin:password@localhost:27017/")
DATABASE_NAME = "portfolio"

# Async client for FastAPI
client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

# Sync client for initial setup
sync_client = MongoClient(MONGODB_URL)
sync_database = sync_client[DATABASE_NAME]

def get_database():
    return database

def get_sync_database():
    return sync_database