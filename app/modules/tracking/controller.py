"""Tracking request handlers."""

import asyncio

from fastapi import WebSocket, WebSocketDisconnect

from app.core.response import api_response
from app.modules.tracking.service import TrackingService
from app.modules.tracking.simulation import simulation_engine
from app.websocket.manager import ws_manager


class TrackingController:
    def __init__(self):
        self.service = TrackingService()

    async def get_tracking(self, bus_id: str):
        data = await self.service.get_tracking(bus_id)
        return api_response(data=data, message="Tracking data retrieved successfully")

    async def websocket_track(self, websocket: WebSocket, bus_id: str) -> None:
        bus_state = await simulation_engine.get_bus_state(bus_id)
        if not bus_state:
            await websocket.accept()
            await websocket.send_json(
                {"error": f"Bus/Route '{bus_id}' not found in active tracking."}
            )
            await websocket.close()
            return

        topic = bus_state["bus_number"]
        queue: asyncio.Queue = asyncio.Queue()
        simulation_engine.register_subscriber(topic, queue)

        await ws_manager.connect(websocket, topic)
        await ws_manager.send_connected(
            websocket,
            {
                "bus_number": bus_state["bus_number"],
                "route_id": bus_state["route_id"],
                "coords": bus_state["coords"],
                "current_stop_index": bus_state["current_stop_index"],
                "next_stop_index": bus_state["next_stop_index"],
                "next_stop_name": bus_state["next_stop_name"],
                "eta_seconds": bus_state["eta_seconds"],
                "direction": bus_state["direction"],
            },
        )

        try:
            while True:
                update_str = await queue.get()
                await websocket.send_text(update_str)
                queue.task_done()
        except WebSocketDisconnect:
            pass
        finally:
            simulation_engine.unregister_subscriber(topic, queue)
            ws_manager.disconnect(websocket, topic)
