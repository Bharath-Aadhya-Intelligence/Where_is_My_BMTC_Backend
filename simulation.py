import os
import asyncio
import logging
import json
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
load_dotenv()

logger = logging.getLogger("simulation")
logging.basicConfig(level=logging.INFO)

STEPS_BETWEEN_STOPS = 10  # 10 steps of 3 seconds = 30 seconds between stops

class BusSimulationEngine:
    def __init__(self):
        self.client = None
        self.db = None
        self.buses_state = {}  # bus_number -> state dict
        self.subscribers = {}  # bus_number/route_id -> set of asyncio.Queue or WebSocket connections
        self.running = False
        self._lock = asyncio.Lock()

    async def initialize(self):
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        db_name = os.getenv("MONGODB_DB", "bmtc")
        logger.info(f"Connecting simulation engine to MongoDB database: {db_name}")
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client[db_name]

        # Fetch buses, stops, and routes
        buses = await self.db["buses"].find().to_list(length=100)
        routes = await self.db["routes"].find().to_list(length=100)
        stops_list = await self.db["stops"].find().to_list(length=100)

        stops_map = {s["stop_name"]: s["location"]["coordinates"] for s in stops_list}
        routes_map = {r["route_id"]: r for r in routes}

        for bus in buses:
            route_id = bus["route_id"]
            route = routes_map.get(route_id)
            if not route:
                continue

            bus_stops = route["stops"]
            stop_coords = []
            for stop_name in bus_stops:
                coords = stops_map.get(stop_name, [77.572, 12.976])
                stop_coords.append({"name": stop_name, "coords": coords})

            self.buses_state[bus["bus_number"]] = {
                "bus_number": bus["bus_number"],
                "route_id": route_id,
                "source": bus["source"],
                "destination": bus["destination"],
                "stops": stop_coords,
                "current_stop_index": 0,
                "next_stop_index": 1,
                "direction": 1,  # 1 = forward, -1 = backward
                "step": 0,
                "coords": stop_coords[0]["coords"],
                "frequency_mins": route["frequency_mins"],
                "operating_hours": route["operating_hours"],
                "next_stop_name": stop_coords[1]["name"],
                "eta_seconds": STEPS_BETWEEN_STOPS * 3
            }
        logger.info(f"Bus simulation engine initialized with {len(self.buses_state)} buses.")

    async def start(self):
        if not self.running:
            self.running = True
            asyncio.create_task(self._simulation_loop())
            logger.info("Bus simulation engine started.")

    async def stop(self):
        self.running = False
        logger.info("Bus simulation engine stopped.")

    async def _simulation_loop(self):
        while self.running:
            try:
                await self._update_positions()
                await self._broadcast_updates()
            except Exception as e:
                logger.error(f"Error in simulation loop: {e}", exc_info=True)
            await asyncio.sleep(3)

    async def _update_positions(self):
        async with self._lock:
            for bus_number, state in self.buses_state.items():
                stops = state["stops"]
                curr_idx = state["current_stop_index"]
                next_idx = state["next_stop_index"]
                step = state["step"]
                direction = state["direction"]

                p1 = stops[curr_idx]["coords"]
                p2 = stops[next_idx]["coords"]

                step += 1
                if step > STEPS_BETWEEN_STOPS:
                    # Reached next stop!
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
                    # Linearly interpolate coords
                    ratio = step / STEPS_BETWEEN_STOPS
                    lon = p1[0] + ratio * (p2[0] - p1[0])
                    lat = p1[1] + ratio * (p2[1] - p1[1])
                    state["step"] = step
                    state["coords"] = [lon, lat]

                remaining_steps = STEPS_BETWEEN_STOPS - step
                state["eta_seconds"] = remaining_steps * 3
                state["next_stop_name"] = stops[next_idx]["name"]

    async def get_bus_state(self, bus_id_or_number: str):
        async with self._lock:
            # check by bus number
            if bus_id_or_number in self.buses_state:
                return self.buses_state[bus_id_or_number]
            # check by route ID
            for state in self.buses_state.values():
                if state["route_id"] == bus_id_or_number:
                    return state
            return None

    async def get_all_buses_state(self):
        async with self._lock:
            return list(self.buses_state.values())

    def register_subscriber(self, topic: str, queue: asyncio.Queue):
        if topic not in self.subscribers:
            self.subscribers[topic] = set()
        self.subscribers[topic].add(queue)

    def unregister_subscriber(self, topic: str, queue: asyncio.Queue):
        if topic in self.subscribers:
            self.subscribers[topic].discard(queue)
            if not self.subscribers[topic]:
                del self.subscribers[topic]

    async def _broadcast_updates(self):
        async with self._lock:
            for topic, queues in list(self.subscribers.items()):
                # A topic can be a bus_number or route_id
                state = None
                if topic in self.buses_state:
                    state = self.buses_state[topic]
                else:
                    for s in self.buses_state.values():
                        if s["route_id"] == topic:
                            state = s
                            break

                if state:
                    payload = {
                        "bus_number": state["bus_number"],
                        "route_id": state["route_id"],
                        "coords": state["coords"],
                        "current_stop_index": state["current_stop_index"],
                        "next_stop_index": state["next_stop_index"],
                        "next_stop_name": state["next_stop_name"],
                        "eta_seconds": state["eta_seconds"],
                        "direction": state["direction"]
                    }
                    data_str = json.dumps(payload)
                    for q in list(queues):
                        try:
                            await q.put(data_str)
                        except Exception as e:
                            logger.error(f"Error putting update in queue: {e}")

# Global singleton
simulation_engine = BusSimulationEngine()
