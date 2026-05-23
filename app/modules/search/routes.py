"""Search API routes."""

from fastapi import APIRouter, Query

from app.modules.search.controller import SearchController

router = APIRouter(prefix="/search", tags=["search"])
controller = SearchController()


@router.get("")
async def search(query: str = Query(..., description="Search query")):
    return await controller.search(query)
