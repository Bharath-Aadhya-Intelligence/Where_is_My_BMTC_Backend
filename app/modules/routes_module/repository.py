"""MongoDB queries for routes collection."""

from typing import Any

from app.core.database import get_database
from app.services.cache_service import CacheService, cache_service


class RouteRepository:
    COLLECTION = "routes"

    async def find_by_id(self, route_id: str) -> dict[str, Any] | None:
        cached = await cache_service.get(CacheService.route_hot_key(route_id))
        if cached:
            return cached

        db = get_database()
        route = await db[self.COLLECTION].find_one({"route_id": route_id}, {"_id": 0})
        if route:
            await cache_service.set(
                CacheService.route_hot_key(route_id),
                route,
                CacheService.TTL_ROUTE_HOT,
            )
        return route

    async def find_all(self, limit: int = 100) -> list[dict[str, Any]]:
        db = get_database()
        return await db[self.COLLECTION].find({}, {"_id": 0}).to_list(length=limit)
