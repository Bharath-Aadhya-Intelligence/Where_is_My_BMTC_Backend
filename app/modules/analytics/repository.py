"""Analytics MongoDB repository."""

from typing import Any

from app.core.database import get_database
from app.utils.helpers import utc_now_iso


class AnalyticsRepository:
    COLLECTION = "analytics"

    async def log_event(self, event: dict[str, Any]) -> None:
        db = get_database()
        event.setdefault("timestamp", utc_now_iso())
        await db[self.COLLECTION].insert_one(event)

    async def popular_routes(self, limit: int = 10) -> list[dict[str, Any]]:
        db = get_database()
        pipeline = [
            {"$match": {"event_type": "search"}},
            {"$group": {"_id": "$query", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {
                "$project": {
                    "_id": 0,
                    "route_id": "$_id",
                    "search_count": "$count",
                }
            },
        ]
        return await db[self.COLLECTION].aggregate(pipeline).to_list(length=limit)
