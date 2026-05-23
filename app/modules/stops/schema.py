"""Pydantic schemas for stops."""

from typing import Any

from pydantic import BaseModel, Field


class StopResponse(BaseModel):
    stop_name: str
    stop_id: str | None = None
    location: dict[str, Any]
    routes_served: list[str] = Field(default_factory=list)
    amenities: list[str] = Field(default_factory=list)


class NearbyStopsResponse(BaseModel):
    stops: list[dict[str, Any]]
    count: int
