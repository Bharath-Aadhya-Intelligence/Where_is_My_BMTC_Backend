"""Redis connection manager with graceful fallback when unavailable."""

import json
import logging
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger("app.redis")


class RedisManager:
    """Async Redis wrapper; operations no-op when Redis is disabled or unreachable."""

    def __init__(self):
        self.client = None
        self._available = False

    @property
    def available(self) -> bool:
        return self._available and self.client is not None

    async def connect(self) -> None:
        settings = get_settings()
        if not settings.REDIS_ENABLED:
            logger.info("Redis disabled via REDIS_ENABLED=false.")
            return

        try:
            import redis.asyncio as redis
        except ImportError:
            logger.warning(
                "Redis package not installed. Run: python3 -m pip install 'redis[hiredis]>=5.0.0' "
                "(or use ./run.sh which installs from requirements.txt)"
            )
            return

        try:
            self.client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2,
            )
            await self.client.ping()
            self._available = True
            logger.info("Redis connection established.")
        except Exception as e:
            logger.warning("Redis unavailable, continuing without cache: %s", e)
            self.client = None
            self._available = False

    async def disconnect(self) -> None:
        if self.client:
            await self.client.close()
            self.client = None
            self._available = False
            logger.info("Redis connection closed.")

    async def get(self, key: str) -> str | None:
        if not self.available:
            return None
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.warning(f"Redis GET failed for {key}: {e}")
            return None

    async def get_json(self, key: str) -> Any | None:
        raw = await self.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        if not self.available:
            return False
        try:
            await self.client.set(key, value, ex=ex)
            return True
        except Exception as e:
            logger.warning(f"Redis SET failed for {key}: {e}")
            return False

    async def set_json(self, key: str, value: Any, ex: int | None = None) -> bool:
        return await self.set(key, json.dumps(value), ex=ex)

    async def delete(self, key: str) -> bool:
        if not self.available:
            return False
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Redis DELETE failed for {key}: {e}")
            return False

    async def publish(self, channel: str, message: str) -> bool:
        if not self.available:
            return False
        try:
            await self.client.publish(channel, message)
            return True
        except Exception as e:
            logger.warning(f"Redis PUBLISH failed for {channel}: {e}")
            return False

    async def zincrby(self, key: str, amount: float, member: str) -> bool:
        if not self.available:
            return False
        try:
            await self.client.zincrby(key, amount, member)
            return True
        except Exception as e:
            logger.warning(f"Redis ZINCRBY failed: {e}")
            return False

    async def zrevrange(self, key: str, start: int, end: int) -> list[str]:
        if not self.available:
            return []
        try:
            return await self.client.zrevrange(key, start, end, withscores=False)
        except Exception as e:
            logger.warning(f"Redis ZREVRANGE failed: {e}")
            return []


redis_manager = RedisManager()
