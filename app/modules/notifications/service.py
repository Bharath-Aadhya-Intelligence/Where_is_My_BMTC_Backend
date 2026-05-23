"""Notification service — placeholder for Firebase/OneSignal."""

import logging
from typing import Any

from app.modules.notifications.schema import NotificationRequest

logger = logging.getLogger("app.notifications")


class NotificationService:
    """Architecture stub for future push notification providers."""

    async def send(self, request: NotificationRequest) -> dict[str, Any]:
        logger.info(
            "Notification [%s] for user=%s bus=%s: %s",
            request.event_type.value,
            request.user_id,
            request.bus_number,
            request.message,
        )
        return {
            "sent": False,
            "provider": "placeholder",
            "event_type": request.event_type.value,
            "message": "Push notifications not yet configured",
        }
