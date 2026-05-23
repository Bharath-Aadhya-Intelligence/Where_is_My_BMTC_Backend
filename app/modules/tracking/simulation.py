"""Bus simulation engine with Redis pub/sub integration."""

import asyncio
import json
import logging
from typing import Any

from app.core.config import get_settings
from app.core.database import get_database
from app.core.redis_client import redis_manager
from app.services.cache_service import CacheService, cache_service
from app.websocket.manager import ws_manager

logger = logging.getLogger("app.simulation")


class BusSimulationEngine:
    def __init__(self):
        self.buses_state: dict[str, dict[str, Any]] = {}
        self.subscribers: dict[str, set[asyncio.Queue]] = {}
        self.running = False
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        settings = get_settings()
        db = get_database()
        steps = settings.SIMULATION_STEPS_BETWEEN_STOPS

        buses = await db["buses"].find().to_list(length=100)
        routes = await db["routes"].find().to_list(length=100)
        stops_list = await db["stops"].find().to_list(length=100)

        stops_map = {
            s["stop_name"]: s["location"]["coordinates"] for s in stops_list
        }
        routes_map = {r["route_id"]: r for r in routes}

        for bus in buses:
            route_id = bus["route_id"]
            route = routes_map.get(route_id)
            if not route:
                continue

            stop_coords = []
            for stop_name in route["stops"]:
                coords = stops_map.get(stop_name, [77.572, 12.976])
                stop_coords.append({"name": stop_name, "coords": coords})

            if len(stop_coords) < 2:
                continue

            self.buses_state[bus["bus_number"]] = {
                "bus_number": bus["bus_number"],
                "route_id": route_id,
                "source": bus.get("source", ""),
                "destination": bus.get("destination", ""),
                "stops": stop_coords,
                "current_stop_index": 0,
                "next_stop_index": 1,
                "direction": 1,
                "step": 0,
                "coords": stop_coords[0]["coords"],
                "frequency_mins": route.get("frequency_mins", 15),
                "operating_hours": route.get("operating_hours", "05:00-23:00"),
                "next_stop_name": stop_coords[1]["name"],
                "eta_seconds": steps * int(settings.SIMULATION_INTERVAL_SECONDS),
                "speed_kmh": 25,
                "heading": 0,
            }

        logger.info(
            "Simulation initialized with %d buses", len(self.buses_state)
        )

    async def start(self) -> None:
        if not self.running:
            self.running = True
            asyncio.create_task(self._simulation_loop())
            logger.info("Bus simulation engine started.")

    async def stop(self) -> None:
        self.running = False
        logger.info("Bus simulation engine stopped.")

    async def _simulation_loop(self) -> None:
        settings = get_settings()
        interval = settings.SIMULATION_INTERVAL_SECONDS
        while self.running:
            try:
                await self._update_positions()
                await self._broadcast_updates()
            except Exception as e:
                logger.error("Error in simulation loop: %s", e, exc_info=True)
            await asyncio.sleep(interval)

    async def _update_positions(self) -> None:
        settings = get_settings()
        steps = settings.SIMULATION_STEPS_BETWEEN_STOPS
        tick_seconds = int(settings.SIMULATION_INTERVAL_SECONDS)

        async with self._lock:
            for state in self.buses_state.values():
                stops = state["stops"]
                curr_idx = state["current_stop_index"]
                next_idx = state["next_stop_index"]
                step = state["step"]
                direction = state["direction"]

                p1 = stops[curr_idx]["coords"]
                p2 = stops[next_idx]["coords"]

                step += 1
                if step > steps:
                    curr_idx = next_idx
                    step = 0

                    if direction == 1:
                        if curr_idx == len(stops) - 1:
                            direction = -1
                            next_idx = curr_idx - 1
                        else:
                            next_idx = curr_idx + 1
                    else:
                        if curr_idx == 0:
                            direction = 1
                            next_idx = 1
                        else:
                            next_idx = curr_idx - 1

                    state["current_stop_index"] = curr_idx
                    state["next_stop_index"] = next_idx
                    state["direction"] = direction
                    state["step"] = step
                    state["coords"] = stops[curr_idx]["coords"]
                else:
                    ratio = step / steps
                    lon = p1[0] + ratio * (p2[0] - p1[0])
                    lat = p1[1] + ratio * (p2[1] - p1[1])
                    state["step"] = step
                    state["coords"] = [lon, lat]

                remaining = steps - step
                state["eta_seconds"] = remaining * tick_seconds
                state["next_stop_name"] = stops[next_idx]["name"]

    async def get_bus_state(self, bus_id_or_number: str) -> dict[str, Any] | None:
        async with self._lock:
            if bus_id_or_number in self.buses_state:
                return dict(self.buses_state[bus_id_or_number])
            for state in self.buses_state.values():
                if state["route_id"] == bus_id_or_number:
                    return dict(state)
            return None

    def register_subscriber(self, topic: str, queue: asyncio.Queue) -> None:
        if topic not in self.subscribers:
            self.subscribers[topic] = set()
        self.subscribers[topic].add(queue)
        ws_manager.register_queue(topic, queue)

    def unregister_subscriber(self, topic: str, queue: asyncio.Queue) -> None:
        if topic in self.subscribers:
            self.subscribers[topic].discard(queue)
            if not self.subscribers[topic]:
                del self.subscribers[topic]
        ws_manager.unregister_queue(topic, queue)

    def _build_payload(self, state: dict[str, Any]) -> dict[str, Any]:
        direction_label = "forward" if state["direction"] == 1 else "backward"
        return {
            "bus_number": state["bus_number"],
            "route_id": state["route_id"],
            "coords": state["coords"],
            "location": {
                "type": "Point",
                "coordinates": state["coords"],
            },
            "current_stop_index": state["current_stop_index"],
            "next_stop_index": state["next_stop_index"],
            "next_stop_name": state["next_stop_name"],
            "eta_seconds": state["eta_seconds"],
            "direction": direction_label,
            "speed_kmh": state.get("speed_kmh", 25),
            "heading": state.get("heading", 0),
        }

    async def _broadcast_updates(self) -> None:
        async with self._lock:
            states = list(self.buses_state.values())

        for state in states:
            payload = self._build_payload(state)
            bus_number = state["bus_number"]
            data_str = json.dumps(payload)

            await cache_service.set(
                CacheService.bus_location_key(bus_number),
                payload,
                CacheService.TTL_BUS_LOCATION,
            )

            channel_bus = f"channel:bus:{bus_number}"
            await redis_manager.publish(channel_bus, data_str)
            await redis_manager.publish("channel:tracking:all", data_str)

            await ws_manager.broadcast_to_topic(bus_number, payload)

            for topic, queues in list(self.subscribers.items()):
                if topic != bus_number and topic != state["route_id"]:
                    continue
                for q in list(queues):
                    try:
                        await q.put(data_str)
                    except Exception as e:
                        logger.error("Queue put failed: %s", e)


simulation_engine = BusSimulationEngine()
