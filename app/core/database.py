"""
MongoDB connection manager using Motor (async driver).
Provides a global singleton for database access.
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings

logger = logging.getLogger("app.database")


class MongoDB:
    """Async MongoDB connection manager."""

    def __init__(self):
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        """Establish connection to MongoDB."""
        settings = get_settings()
        logger.info(f"Connecting to MongoDB database: {settings.MONGODB_DB}")
        # Atlas-friendly pool: minPoolSize=0 avoids stale background reconnect/auth errors.
        self.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            maxPoolSize=50,
            minPoolSize=0,
            maxIdleTimeMS=45_000,
            serverSelectionTimeoutMS=10_000,
            connectTimeoutMS=10_000,
            socketTimeoutMS=20_000,
            waitQueueTimeoutMS=10_000,
            retryWrites=True,
            retryReads=True,
        )
        self.db = self.client[settings.MONGODB_DB]

        # Verify connection
        try:
            await self.client.admin.command("ping")
            logger.info("MongoDB connection established successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("MongoDB connection closed.")

    def get_collection(self, name: str):
        """Get a MongoDB collection by name."""
        if self.db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.db[name]


# Global singleton
mongodb = MongoDB()


def get_database() -> AsyncIOMotorDatabase:
    """Get the active database instance."""
    if mongodb.db is None:
        raise RuntimeError("Database not connected. Call connect() first.")
    return mongodb.db
