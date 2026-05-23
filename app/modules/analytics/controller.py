"""Analytics request handlers."""

from app.core.response import api_response
from app.modules.analytics.service import AnalyticsService


class AnalyticsController:
    def __init__(self):
        self.service = AnalyticsService()

    async def popular_routes(self):
        routes = await self.service.get_popular_routes()
        return api_response(
            data={"routes": routes},
            message="Popular routes retrieved successfully",
        )

    async def popular_searches(self):
        searches = await self.service.get_popular_searches()
        return api_response(
            data={"searches": searches},
            message="Popular searches retrieved successfully",
        )
