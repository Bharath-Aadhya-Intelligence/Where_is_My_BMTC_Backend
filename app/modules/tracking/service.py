"""Tracking business logic."""

from typing import Any

from app.core.exceptions import NotFoundException
from app.modules.tracking.repository import TrackingRepository
from app.modules.tracking.simulation import simulation_engine
from app.services.cache_service import CacheService, cache_service


class TrackingService:
    def __init__(self):
        self.repo = TrackingRepository()

    async def get_tracking(self, bus_id: str) -> dict[str, Any]:
        cached = await cache_service.get(CacheService.bus_location_key(bus_id))
        if cached:
            return cached

        state = await simulation_engine.get_bus_state(bus_id)
        if state:
            payload = {
                "bus_number": state["bus_number"],
                "route_id": state["route_id"],
                "location": {
                    "type": "Point",
                    "coordinates": state["coords"],
                },
                "speed_kmh": state.get("speed_kmh", 25),
                "heading": state.get("heading", 0),
                "current_stop_index": state["current_stop_index"],
                "next_stop": state.get("next_stop_name"),
                "eta_seconds": state["eta_seconds"],
                "direction": "forward" if state["direction"] == 1 else "backward",
            }
            await cache_service.set(
                CacheService.bus_location_key(state["bus_number"]),
                payload,
                CacheService.TTL_BUS_LOCATION,
            )
            return payload

        doc = await self.repo.find_by_bus(bus_id)
        if doc:
            return doc

        raise NotFoundException(
            f"Bus or route '{bus_id}' not found in active tracking"
        )
