"""Notification schemas (placeholder for push integration)."""

from enum import Enum

from pydantic import BaseModel, Field


class NotificationEventType(str, Enum):
    BUS_ARRIVAL = "bus_arrival"
    DELAY_ALERT = "delay_alert"
    ROUTE_DIVERSION = "route_diversion"


class NotificationRequest(BaseModel):
    user_id: str
    bus_number: str
    event_type: NotificationEventType
    message: str = ""
    metadata: dict = Field(default_factory=dict)
