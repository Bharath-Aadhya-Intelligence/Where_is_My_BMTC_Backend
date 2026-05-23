"""Pydantic schemas for buses module."""

from typing import Any

from pydantic import BaseModel, Field


class BusResponse(BaseModel):
    bus_number: str
    source: str
    destination: str
    route_id: str
    bus_type: str = "standard"
    status: str = "active"


class BusDetailResponse(BusResponse):
    stops: list[dict[str, Any]] = Field(default_factory=list)
    frequency_mins: int = 15
    operating_hours: str = "05:00-23:00"


class BusListResponse(BaseModel):
    buses: list[BusResponse]
    count: int
