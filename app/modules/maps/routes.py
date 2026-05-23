"""Maps API routes."""

from fastapi import APIRouter

from app.modules.maps.controller import MapsController

router = APIRouter(prefix="/maps", tags=["maps"])
controller = MapsController()


@router.get("/route/{route_id}")
async def route_map(route_id: str):
    return await controller.route_map(route_id)
