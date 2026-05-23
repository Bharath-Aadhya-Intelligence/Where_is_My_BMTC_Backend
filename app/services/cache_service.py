"""Redis caching abstraction."""

import functools
import logging
from typing import Any, Callable

from app.core.redis import redis_manager

logger = logging.getLogger("app.cache")


class CacheService:
    TTL_BUS_LOCATION = 30
    TTL_ETA = 15
    TTL_ROUTE_HOT = 300
    TTL_ANALYTICS_SEARCH = 3600

    KEY_BUS_LOCATION = "bus:location:{bus_number}"
    KEY_ETA = "eta:{bus_id}:{stop}"
    KEY_ROUTE_HOT = "route:hot:{route_id}"
    KEY_POPULAR_SEARCHES = "analytics:search:popular"

    @staticmethod
    def bus_location_key(bus_number: str) -> str:
        return CacheService.KEY_BUS_LOCATION.format(bus_number=bus_number)

    @staticmethod
    def eta_key(bus_id: str, stop: str) -> str:
        return CacheService.KEY_ETA.format(bus_id=bus_id, stop=stop)

    @staticmethod
    def route_hot_key(route_id: str) -> str:
        return CacheService.KEY_ROUTE_HOT.format(route_id=route_id)

    async def get(self, key: str) -> Any | None:
        return await redis_manager.get_json(key)

    async def set(self, key: str, value: Any, ttl: int) -> bool:
        return await redis_manager.set_json(key, value, ex=ttl)

    async def invalidate(self, key: str) -> bool:
        return await redis_manager.delete(key)

    async def record_popular_search(self, query: str) -> None:
        await redis_manager.zincrby(
            self.KEY_POPULAR_SEARCHES, 1.0, query.lower().strip()
        )

    async def get_popular_searches(self, limit: int = 10) -> list[str]:
        return await redis_manager.zrevrange(self.KEY_POPULAR_SEARCHES, 0, limit - 1)


cache_service = CacheService()


def cache(ttl: int, key_builder: Callable[..., str]):
    """Decorator to cache async function results in Redis."""

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = key_builder(*args, **kwargs)
            cached = await cache_service.get(key)
            if cached is not None:
                return cached
            result = await func(*args, **kwargs)
            if result is not None:
                await cache_service.set(key, result, ttl)
            return result

        return wrapper

    return decorator
