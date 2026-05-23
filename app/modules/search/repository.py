"""Search queries across collections."""

from typing import Any

from app.core.database import get_database


class SearchRepository:
    async def search_buses(self, query: str) -> list[dict[str, Any]]:
        db = get_database()
        search_filter = {
            "$or": [
                {"bus_number": {"$regex": query, "$options": "i"}},
                {"source": {"$regex": query, "$options": "i"}},
                {"destination": {"$regex": query, "$options": "i"}},
                {"route_id": {"$regex": query, "$options": "i"}},
            ]
        }
        return await db["buses"].find(search_filter, {"_id": 0}).to_list(length=100)

    async def search_routes(self, query: str) -> list[dict[str, Any]]:
        db = get_database()
        return await db["routes"].find(
            {
                "$or": [
                    {"route_id": {"$regex": query, "$options": "i"}},
                    {"stops": {"$regex": query, "$options": "i"}},
                ]
            },
            {"_id": 0},
        ).to_list(length=50)

    async def search_stops(self, query: str) -> list[dict[str, Any]]:
        db = get_database()
        return await db["stops"].find(
            {"stop_name": {"$regex": query, "$options": "i"}},
            {"_id": 0},
        ).to_list(length=50)
