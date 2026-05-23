"""Business logic for buses."""

from typing import Any

from app.core.exceptions import NotFoundException
from app.modules.buses.repository import BusRepository
from app.modules.routes_module.repository import RouteRepository
from app.modules.stops.repository import StopRepository


class BusService:
    def __init__(self):
        self.bus_repo = BusRepository()
        self.route_repo = RouteRepository()
        self.stop_repo = StopRepository()

    async def list_buses(self) -> list[dict[str, Any]]:
        return await self.bus_repo.find_all()

    async def get_bus_details(self, bus_number: str) -> dict[str, Any]:
        bus = await self.bus_repo.find_by_number(bus_number)
        if not bus:
            raise NotFoundException(f"Bus with number {bus_number} not found")

        route = await self.route_repo.find_by_id(bus["route_id"])
        if not route:
            bus["stops"] = []
            bus["frequency_mins"] = 0
            bus["operating_hours"] = "N/A"
            return bus

        stops_details = []
        for stop_name in route.get("stops", []):
            stop_doc = await self.stop_repo.find_by_name(stop_name)
            if stop_doc:
                stops_details.append(stop_doc)
            else:
                stops_details.append(
                    {
                        "stop_name": stop_name,
                        "location": {
                            "type": "Point",
                            "coordinates": [77.572, 12.976],
                        },
                    }
                )

        bus["stops"] = stops_details
        bus["frequency_mins"] = route.get("frequency_mins", 15)
        bus["operating_hours"] = route.get("operating_hours", "05:00-23:00")
        return bus
