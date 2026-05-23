"""WebSocket event type definitions."""

from enum import Enum


class WSEventType(str, Enum):
    SUBSCRIBE_BUS = "subscribe_bus"
    BUS_LOCATION = "bus_location"
    ETA_UPDATE = "eta_update"
    BUS_ARRIVED = "bus_arrived"
    CONNECTED = "connected"
    ERROR = "error"
