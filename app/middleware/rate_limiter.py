"""Simple in-memory rate limiter per client IP."""

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import get_settings


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in ("/health", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        settings = get_settings()
        limit = settings.RATE_LIMIT_PER_MINUTE
        ip = self._client_ip(request)
        now = time.time()
        window_start = now - 60

        timestamps = [t for t in self._requests[ip] if t > window_start]
        if len(timestamps) >= limit:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {limit} requests per minute",
                },
            )

        timestamps.append(now)
        self._requests[ip] = timestamps
        return await call_next(request)
