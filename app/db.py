import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from dotenv import load_dotenv

load_dotenv()

_MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
_DB_NAME: str = os.getenv("DB_NAME", "assessment_db")
_COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "employees")

_mongo_client: Optional[AsyncIOMotorClient] = None


async def connect_to_mongo() -> None:
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(_MONGODB_URI)
        await get_employees_collection().create_index("employee_id", unique=True)
        await get_employees_collection().create_index([("department", 1), ("joining_date", -1)])
        await get_employees_collection().create_index("skills")


async def disconnect_from_mongo() -> None:
    global _mongo_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None


def get_employees_collection() -> AsyncIOMotorCollection:
    if _mongo_client is None:
        raise RuntimeError("Mongo client not initialized. Call connect_to_mongo() first.")
    return _mongo_client[_DB_NAME][_COLLECTION_NAME]