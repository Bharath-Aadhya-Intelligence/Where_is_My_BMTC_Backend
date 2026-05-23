"""Business logic for stops."""

from typing import Any

from app.modules.stops.repository import StopRepository
from app.utils.validators import validate_coordinates, validate_radius


class StopService:
    def __init__(self):
        self.repo = StopRepository()

    async def get_nearby(
        self, lat: float, lng: float, radius: float = 1000
    ) -> list[dict[str, Any]]:
        validate_coordinates(lat, lng)
        validate_radius(radius)
        return await self.repo.find_nearby(lat, lng, radius)
