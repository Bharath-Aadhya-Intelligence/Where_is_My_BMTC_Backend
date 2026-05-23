"""Search response schemas."""

from typing import Any

from pydantic import BaseModel, Field


class SearchResponse(BaseModel):
    query: str
    buses: list[dict[str, Any]] = Field(default_factory=list)
    routes: list[dict[str, Any]] = Field(default_factory=list)
    stops: list[dict[str, Any]] = Field(default_factory=list)
    total_count: int
