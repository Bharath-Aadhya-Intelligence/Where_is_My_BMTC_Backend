import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from simulation import simulation_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize and start the live simulation engine
    await simulation_engine.initialize()
    await simulation_engine.start()
    app.state.db = simulation_engine.db
    yield
    # Shutdown: Stop the simulation engine
    await simulation_engine.stop()

app = FastAPI(
    title="Where Is My BMTC API",
    description="Real-time transit tracking and route query API for BMTC buses in Bengaluru.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "Where is My BMTC API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Where is My BMTC API is fully functional"}

@app.get("/buses")
async def list_buses():
    db = app.state.db
    try:
        buses = await db["buses"].find({}, {"_id": 0}).to_list(length=100)
        return buses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search_buses(query: str = Query(..., description="Query by bus number or route details")):
    db = app.state.db
    try:
        search_filter = {
            "$or": [
                {"bus_number": {"$regex": query, "$options": "i"}},
                {"source": {"$regex": query, "$options": "i"}},
                {"destination": {"$regex": query, "$options": "i"}},
                {"route_id": {"$regex": query, "$options": "i"}}
            ]
        }
        buses = await db["buses"].find(search_filter, {"_id": 0}).to_list(length=100)
        return buses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bus/{bus_number}")
async def get_bus_details(bus_number: str):
    db = app.state.db
    try:
        bus = await db["buses"].find_one({"bus_number": bus_number}, {"_id": 0})
        if not bus:
            raise HTTPException(status_code=404, detail=f"Bus with number {bus_number} not found")

        route = await db["routes"].find_one({"route_id": bus["route_id"]}, {"_id": 0})
        if not route:
            bus["stops"] = []
            bus["frequency_mins"] = 0
            bus["operating_hours"] = "N/A"
            return bus

        stops_details = []
        for stop_name in route["stops"]:
            stop_doc = await db["stops"].find_one({"stop_name": stop_name}, {"_id": 0})
            if stop_doc:
                stops_details.append(stop_doc)
            else:
                stops_details.append({
                    "stop_name": stop_name,
                    "location": {
                        "type": "Point",
                        "coordinates": [77.572, 12.976]
                    }
                })

        bus["stops"] = stops_details
        bus["frequency_mins"] = route.get("frequency_mins", 15)
        bus["operating_hours"] = route.get("operating_hours", "05:00-23:00")
        return bus
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stops/nearby")
async def get_nearby_stops(
    lat: float = Query(..., description="Latitude of user's current location"),
    lng: float = Query(..., description="Longitude of user's current location")
):
    db = app.state.db
    try:
        query = {
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [lng, lat]
                    },
                    "$maxDistance": 1000  # 1 km in meters
                }
            }
        }
        stops = await db["stops"].find(query, {"_id": 0}).to_list(length=100)
        return stops
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/track/{bus_id}")
async def track_bus(websocket: WebSocket, bus_id: str):
    await websocket.accept()
    
    # We want to support bus_id matching either bus_number or route_id
    # Let's verify that the bus exists
    bus_state = await simulation_engine.get_bus_state(bus_id)
    if not bus_state:
        await websocket.send_json({"error": f"Bus/Route '{bus_id}' not found in active tracking."})
        await websocket.close()
        return

    # Use an asyncio Queue to listen to real-time simulation ticks
    queue = asyncio.Queue()
    # We will register for the matched bus number to ensure uniform updates
    topic = bus_state["bus_number"]
    simulation_engine.register_subscriber(topic, queue)
    
    # Immediately send the current status to initialize client UI state
    await websocket.send_json({
        "status": "connected",
        "bus_number": bus_state["bus_number"],
        "route_id": bus_state["route_id"],
        "coords": bus_state["coords"],
        "current_stop_index": bus_state["current_stop_index"],
        "next_stop_index": bus_state["next_stop_index"],
        "next_stop_name": bus_state["next_stop_name"],
        "eta_seconds": bus_state["eta_seconds"],
        "direction": bus_state["direction"]
    })

    try:
        while True:
            # Wait for coordinate updates from the simulation queue
            update_str = await queue.get()
            await websocket.send_text(update_str)
            queue.task_done()
    except WebSocketDisconnect:
        pass
    finally:
        simulation_engine.unregister_subscriber(topic, queue)
