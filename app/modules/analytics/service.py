"""Analytics business logic."""

from typing import Any

from app.modules.analytics.repository import AnalyticsRepository
from app.services.cache_service import cache_service


class AnalyticsService:
    def __init__(self):
        self.repo = AnalyticsRepository()

    async def log_search(self, query: str, result_count: int) -> None:
        await self.repo.log_event(
            {
                "event_type": "search",
                "query": query,
                "result_count": result_count,
                "metadata": {},
            }
        )

    async def log_route_view(self, route_id: str) -> None:
        await self.repo.log_event(
            {
                "event_type": "route_view",
                "query": route_id,
                "result_count": 1,
                "metadata": {"route_id": route_id},
            }
        )

    async def get_popular_routes(self, limit: int = 10) -> list[dict[str, Any]]:
        return await self.repo.popular_routes(limit)

    async def get_popular_searches(self, limit: int = 10) -> list[str]:
        redis_results = await cache_service.get_popular_searches(limit)
        if redis_results:
            return redis_results
        routes = await self.repo.popular_routes(limit)
        return [r.get("route_id", "") for r in routes if r.get("route_id")]
