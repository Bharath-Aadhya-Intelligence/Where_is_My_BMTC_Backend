"""Search request handlers."""

from app.core.response import api_response
from app.modules.search.service import SearchService


class SearchController:
    def __init__(self):
        self.service = SearchService()

    async def search(self, query: str):
        results = await self.service.search(query)
        return api_response(data=results, message="Search completed successfully")
