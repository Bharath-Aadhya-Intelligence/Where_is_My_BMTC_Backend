"""Search business logic."""

from typing import Any

from app.modules.analytics.service import AnalyticsService
from app.modules.search.repository import SearchRepository
from app.services.cache_service import cache_service


class SearchService:
    def __init__(self):
        self.repo = SearchRepository()
        self.analytics = AnalyticsService()

    async def search(self, query: str) -> dict[str, Any]:
        query = query.strip()
        buses = await self.repo.search_buses(query)
        routes = await self.repo.search_routes(query)
        stops = await self.repo.search_stops(query)
        total = len(buses) + len(routes) + len(stops)

        await cache_service.record_popular_search(query)
        await self.analytics.log_search(query, total)

        return {
            "query": query,
            "buses": buses,
            "routes": routes,
            "stops": stops,
            "total_count": total,
        }
