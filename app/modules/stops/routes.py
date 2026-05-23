"""Stops API routes."""

from fastapi import APIRouter, Query

from app.modules.stops.controller import StopController

router = APIRouter(prefix="/stops", tags=["stops"])
controller = StopController()


@router.get("/nearby")
async def nearby_stops(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius: float = Query(1000, description="Search radius in meters"),
):
    return await controller.nearby(lat, lng, radius)
