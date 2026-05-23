"""Buses API routes."""

from fastapi import APIRouter

from app.modules.buses.controller import BusController

router = APIRouter(prefix="/buses", tags=["buses"])
controller = BusController()


@router.get("")
async def list_buses():
    return await controller.list_buses()


@router.get("/{bus_number}")
async def get_bus(bus_number: str):
    return await controller.get_bus(bus_number)
