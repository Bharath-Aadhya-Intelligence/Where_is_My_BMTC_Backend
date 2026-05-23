"""WebSocket connection manager with room-based subscriptions."""

import asyncio
import json
import logging
from typing import Any

from fastapi import WebSocket

from app.websocket.events import WSEventType

logger = logging.getLogger("app.websocket")


class WebSocketManager:
    """Manages WebSocket connections grouped by bus topic."""

    def __init__(self):
        self._connections: dict[str, set[WebSocket]] = {}
        self._local_queues: dict[str, set[asyncio.Queue]] = {}

    async def connect(self, websocket: WebSocket, topic: str) -> None:
        await websocket.accept()
        if topic not in self._connections:
            self._connections[topic] = set()
        self._connections[topic].add(websocket)

    def disconnect(self, websocket: WebSocket, topic: str) -> None:
        if topic in self._connections:
            self._connections[topic].discard(websocket)
            if not self._connections[topic]:
                del self._connections[topic]

    def register_queue(self, topic: str, queue: asyncio.Queue) -> None:
        if topic not in self._local_queues:
            self._local_queues[topic] = set()
        self._local_queues[topic].add(queue)

    def unregister_queue(self, topic: str, queue: asyncio.Queue) -> None:
        if topic in self._local_queues:
            self._local_queues[topic].discard(queue)
            if not self._local_queues[topic]:
                del self._local_queues[topic]

    async def broadcast_to_topic(self, topic: str, payload: dict[str, Any]) -> None:
        message = json.dumps(payload)
        for ws in list(self._connections.get(topic, set())):
            try:
                await ws.send_text(message)
            except Exception as e:
                logger.warning("WebSocket send failed: %s", e)
                self.disconnect(ws, topic)

        for queue in list(self._local_queues.get(topic, set())):
            try:
                await queue.put(message)
            except Exception as e:
                logger.warning("Queue put failed: %s", e)

    async def send_connected(self, websocket: WebSocket, data: dict[str, Any]) -> None:
        await websocket.send_json(
            {"event": WSEventType.CONNECTED.value, **data}
        )


ws_manager = WebSocketManager()
