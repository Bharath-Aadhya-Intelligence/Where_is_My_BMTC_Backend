"""ETA API routes."""

from fastapi import APIRouter, Query

from app.modules.eta.controller import ETAController

router = APIRouter(prefix="/eta", tags=["eta"])
controller = ETAController()


@router.get("/{bus_id}")
async def get_eta(
    bus_id: str,
    stop: str | None = Query(None, description="Optional target stop name"),
):
    return await controller.get_eta(bus_id, stop)
