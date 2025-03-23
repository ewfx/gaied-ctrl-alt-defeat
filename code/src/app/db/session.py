from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from ..core.config import settings
# from ..schemas.request_types import RequestTypeSchema, SubRequestTypeSchema

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.DB_NAME]

async def init_db():
    try:
        # Run a test query to check the connection
        print(settings.MONGO_URI)
        await db.command("ping")
        # await init_beanie(db, document_models=[RequestTypeSchema, SubRequestTypeSchema])
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"❌ MongoDB connection error: {e}")

async def close_db():
    try:
        client.close()
        print("✅ MongoDB connection closed")
    except Exception as e:
        print(f"❌ MongoDB disconnection error: {e}")

