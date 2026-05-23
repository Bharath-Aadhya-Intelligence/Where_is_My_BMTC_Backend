"""Tracking schemas."""

from typing import Any

from pydantic import BaseModel, Field


class TrackingResponse(BaseModel):
    bus_number: str
    route_id: str
    location: dict[str, Any]
    speed_kmh: float = 0
    heading: float = 0
    current_stop_index: int = 0
    next_stop: str | None = None
    eta_seconds: int = 0
    direction: str = "forward"
