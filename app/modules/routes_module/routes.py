"""Routes API."""

from fastapi import APIRouter

from app.modules.routes_module.controller import RouteController

router = APIRouter(prefix="/routes", tags=["routes"])
controller = RouteController()


@router.get("/{route_id}")
async def get_route(route_id: str):
    return await controller.get_route(route_id)
