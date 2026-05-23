"""Maps module schemas."""

from typing import Any

from pydantic import BaseModel, Field


class RouteMapResponse(BaseModel):
    route_id: str
    coordinates: list[list[float]] = Field(default_factory=list)
    stop_markers: list[dict[str, Any]] = Field(default_factory=list)
