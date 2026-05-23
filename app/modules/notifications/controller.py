"""Notification request handlers."""

from app.core.response import api_response
from app.modules.notifications.schema import NotificationRequest
from app.modules.notifications.service import NotificationService


class NotificationController:
    def __init__(self):
        self.service = NotificationService()

    async def send(self, body: NotificationRequest):
        result = await self.service.send(body)
        return api_response(
            data=result,
            message="Notification request accepted",
            status_code=202,
        )
