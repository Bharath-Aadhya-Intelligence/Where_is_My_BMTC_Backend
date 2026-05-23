"""ETA request handlers."""

from app.core.response import api_response
from app.modules.eta.service import ETAService


class ETAController:
    def __init__(self):
        self.service = ETAService()

    async def get_eta(self, bus_id: str, stop: str | None = None):
        data = await self.service.get_eta(bus_id, stop)
        return api_response(data=data, message="ETA calculated successfully")
