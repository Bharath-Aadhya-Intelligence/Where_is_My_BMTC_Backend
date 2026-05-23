"""Live tracking MongoDB repository."""

from typing import Any

from app.core.database import get_database
from app.utils.helpers import utc_now_iso


class TrackingRepository:
    COLLECTION = "live_tracking"

    async def upsert(self, tracking: dict[str, Any]) -> None:
        db = get_database()
        tracking["timestamp"] = utc_now_iso()
        await db[self.COLLECTION].update_one(
            {"bus_number": tracking["bus_number"]},
            {"$set": tracking},
            upsert=True,
        )

    async def find_by_bus(self, bus_number: str) -> dict[str, Any] | None:
        db = get_database()
        return await db[self.COLLECTION].find_one(
            {"bus_number": bus_number}, {"_id": 0}
        )
