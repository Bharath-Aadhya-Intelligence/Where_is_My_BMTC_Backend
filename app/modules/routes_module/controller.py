"""Request handlers for routes."""

from app.core.response import api_response
from app.modules.routes_module.service import RouteService


class RouteController:
    def __init__(self):
        self.service = RouteService()

    async def get_route(self, route_id: str):
        route = await self.service.get_route(route_id)
        return api_response(data=route, message="Route retrieved successfully")
