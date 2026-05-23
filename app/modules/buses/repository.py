"""MongoDB queries for buses collection."""

from typing import Any

from app.core.database import get_database


class BusRepository:
    COLLECTION = "buses"

    async def find_all(self, limit: int = 100) -> list[dict[str, Any]]:
        db = get_database()
        return await db[self.COLLECTION].find({}, {"_id": 0}).to_list(length=limit)

    async def find_by_number(self, bus_number: str) -> dict[str, Any] | None:
        db = get_database()
        return await db[self.COLLECTION].find_one(
            {"bus_number": bus_number}, {"_id": 0}
        )

    async def find_by_route(self, route_id: str) -> list[dict[str, Any]]:
        db = get_database()
        return await db[self.COLLECTION].find(
            {"route_id": route_id}, {"_id": 0}
        ).to_list(length=100)
