"""ETA calculation service."""

from typing import Any

from app.core.exceptions import NotFoundException
from app.modules.stops.repository import StopRepository
from app.modules.tracking.simulation import simulation_engine
from app.services.cache_service import CacheService, cache_service
from app.services.geo_service import eta_seconds_from_distance_km, extract_lat_lng, haversine_km


class ETAService:
    def __init__(self):
        self.stop_repo = StopRepository()

    async def get_eta(
        self, bus_id: str, stop_name: str | None = None
    ) -> dict[str, Any]:
        cache_key = CacheService.eta_key(
            bus_id, stop_name or "_next"
        )
        cached = await cache_service.get(cache_key)
        if cached:
            return cached

        state = await simulation_engine.get_bus_state(bus_id)
        if not state:
            raise NotFoundException(f"Bus '{bus_id}' not found for ETA")

        bus_lat, bus_lng = state["coords"][1], state["coords"][0]
        target_stop = stop_name or state.get("next_stop_name")

        if stop_name:
            stop_doc = await self.stop_repo.find_by_name(stop_name)
            if not stop_doc:
                raise NotFoundException(f"Stop '{stop_name}' not found")
            stop_lat, stop_lng = extract_lat_lng(stop_doc["location"])
            distance_km = haversine_km(bus_lat, bus_lng, stop_lat, stop_lng)
            eta_seconds = eta_seconds_from_distance_km(
                distance_km, state.get("speed_kmh", 25)
            )
        else:
            eta_seconds = state.get("eta_seconds", 0)
            distance_km = None

        result = {
            "bus_id": state["bus_number"],
            "next_stop": state.get("next_stop_name"),
            "target_stop": target_stop,
            "eta_seconds": eta_seconds,
            "distance_km": distance_km,
        }

        await cache_service.set(cache_key, result, CacheService.TTL_ETA)
        return result
