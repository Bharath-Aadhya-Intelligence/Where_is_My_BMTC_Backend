"""ETA schemas."""

from pydantic import BaseModel


class ETAResponse(BaseModel):
    bus_id: str
    next_stop: str | None = None
    target_stop: str | None = None
    eta_seconds: int
    distance_km: float | None = None
