"""Tracking API routes."""

from fastapi import APIRouter, WebSocket

from app.modules.tracking.controller import TrackingController

router = APIRouter(prefix="/tracking", tags=["tracking"])
controller = TrackingController()


@router.get("/{bus_id}")
async def get_tracking(bus_id: str):
    return await controller.get_tracking(bus_id)


def register_ws_routes(app) -> None:
    @app.websocket("/ws/track/{bus_id}")
    async def track_bus_ws(websocket: WebSocket, bus_id: str):
        await controller.websocket_track(websocket, bus_id)
