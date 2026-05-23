"""MongoDB queries for stops collection."""

from typing import Any

from app.core.database import get_database


class StopRepository:
    COLLECTION = "stops"

    async def find_by_name(self, stop_name: str) -> dict[str, Any] | None:
        db = get_database()
        return await db[self.COLLECTION].find_one(
            {"stop_name": stop_name}, {"_id": 0}
        )

    async def find_nearby(
        self, lat: float, lng: float, radius_m: float = 1000
    ) -> list[dict[str, Any]]:
        db = get_database()
        query = {
            "location": {
                "$near": {
                    "$geometry": {"type": "Point", "coordinates": [lng, lat]},
                    "$maxDistance": radius_m,
                }
            }
        }
        return await db[self.COLLECTION].find(query, {"_id": 0}).to_list(length=100)

    async def search_by_name(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        db = get_database()
        return await db[self.COLLECTION].find(
            {"stop_name": {"$regex": query, "$options": "i"}},
            {"_id": 0},
        ).to_list(length=limit)
