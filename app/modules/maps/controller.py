"""Maps request handlers."""

from app.core.response import api_response
from app.modules.maps.service import MapsService


class MapsController:
    def __init__(self):
        self.service = MapsService()

    async def route_map(self, route_id: str):
        data = await self.service.get_route_map(route_id)
        return api_response(data=data, message="Route map data retrieved successfully")
