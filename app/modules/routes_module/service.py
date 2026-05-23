"""Business logic for routes."""

from typing import Any

from app.core.exceptions import NotFoundException
from app.modules.routes_module.repository import RouteRepository
from app.modules.stops.repository import StopRepository
from app.services.geo_service import geojson_point


class RouteService:
    def __init__(self):
        self.route_repo = RouteRepository()
        self.stop_repo = StopRepository()

    async def get_route(self, route_id: str) -> dict[str, Any]:
        route = await self.route_repo.find_by_id(route_id)
        if not route:
            raise NotFoundException(f"Route {route_id} not found")

        if not route.get("polyline"):
            polyline = []
            for stop_name in route.get("stops", []):
                stop = await self.stop_repo.find_by_name(stop_name)
                if stop and stop.get("location"):
                    polyline.append(stop["location"])
                else:
                    polyline.append(geojson_point(77.572, 12.976))
            route["polyline"] = polyline

        route.setdefault("direction", "up")
        return route
