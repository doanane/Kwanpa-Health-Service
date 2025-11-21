from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

MONGO_DETAILS = "mongodb://admin:password@localhost:27017/"
DATABASE_NAME = "portfolio"

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client[DATABASE_NAME]

sync_client = MongoClient(MONGO_DETAILS)
sync_database = sync_client[DATABASE_NAME]

def get_database():
    return database

def get_sync_database():
    return sync_database