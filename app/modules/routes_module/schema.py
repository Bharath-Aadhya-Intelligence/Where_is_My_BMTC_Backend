"""Pydantic schemas for routes module."""

from typing import Any

from pydantic import BaseModel, Field


class RouteResponse(BaseModel):
    route_id: str
    stops: list[str] = Field(default_factory=list)
    polyline: list[dict[str, Any]] = Field(default_factory=list)
    frequency_mins: int = 15
    operating_hours: str = "05:00-23:00"
    direction: str = "up"
    total_distance_km: float | None = None
