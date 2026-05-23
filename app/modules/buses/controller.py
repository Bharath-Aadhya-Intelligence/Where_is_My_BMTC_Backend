"""Request handlers for buses."""

from app.core.response import api_response
from app.modules.buses.service import BusService


class BusController:
    def __init__(self):
        self.service = BusService()

    async def list_buses(self):
        buses = await self.service.list_buses()
        return api_response(
            data={"buses": buses, "count": len(buses)},
            message="Buses retrieved successfully",
        )

    async def get_bus(self, bus_number: str):
        bus = await self.service.get_bus_details(bus_number)
        return api_response(data=bus, message="Bus details retrieved successfully")
