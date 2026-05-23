"""Request handlers for stops."""

from app.core.response import api_response
from app.modules.stops.service import StopService


class StopController:
    def __init__(self):
        self.service = StopService()

    async def nearby(self, lat: float, lng: float, radius: float = 1000):
        stops = await self.service.get_nearby(lat, lng, radius)
        return api_response(
            data={"stops": stops, "count": len(stops)},
            message="Nearby stops retrieved successfully",
        )
