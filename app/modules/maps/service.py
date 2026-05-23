"""Map rendering data service."""

from typing import Any

from app.core.exceptions import NotFoundException
from app.modules.routes_module.service import RouteService
from app.modules.stops.repository import StopRepository
from app.services.geo_service import extract_lat_lng


class MapsService:
    def __init__(self):
        self.route_service = RouteService()
        self.stop_repo = StopRepository()

    async def get_route_map(self, route_id: str) -> dict[str, Any]:
        route = await self.route_service.get_route(route_id)
        if not route:
            raise NotFoundException(f"Route {route_id} not found")

        coordinates: list[list[float]] = []
        stop_markers: list[dict[str, Any]] = []

        for stop_name in route.get("stops", []):
            stop = await self.stop_repo.find_by_name(stop_name)
            if stop and stop.get("location"):
                lat, lng = extract_lat_lng(stop["location"])
                coordinates.append([lng, lat])
                stop_markers.append(
                    {
                        "stop_name": stop_name,
                        "coordinates": [lng, lat],
                        "location": stop["location"],
                    }
                )
            else:
                coordinates.append([77.572, 12.976])
                stop_markers.append(
                    {
                        "stop_name": stop_name,
                        "coordinates": [77.572, 12.976],
                    }
                )

        return {
            "route_id": route_id,
            "coordinates": coordinates,
            "stop_markers": stop_markers,
        }
