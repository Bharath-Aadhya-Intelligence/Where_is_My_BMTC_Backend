"""Analytics schemas."""

from pydantic import BaseModel, Field


class PopularRoutesResponse(BaseModel):
    routes: list[dict] = Field(default_factory=list)


class PopularSearchesResponse(BaseModel):
    searches: list[str] = Field(default_factory=list)
