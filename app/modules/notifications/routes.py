"""Notifications API routes."""

from fastapi import APIRouter

from app.modules.notifications.controller import NotificationController
from app.modules.notifications.schema import NotificationRequest

router = APIRouter(prefix="/notifications", tags=["notifications"])
controller = NotificationController()


@router.post("/send")
async def send_notification(body: NotificationRequest):
    return await controller.send(body)
