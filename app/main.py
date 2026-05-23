"""FastAPI application factory and lifespan."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.database import mongodb
from app.core.redis import redis_manager
from app.core.response import api_response
from app.middleware.cors import setup_cors
from app.middleware.error_handler import register_exception_handlers
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.modules.analytics.routes import router as analytics_router
from app.modules.buses.routes import router as buses_router
from app.modules.eta.routes import router as eta_router
from app.modules.maps.routes import router as maps_router
from app.modules.notifications.routes import router as notifications_router
from app.modules.routes_module.routes import router as routes_router
from app.modules.search.routes import router as search_router
from app.modules.stops.routes import router as stops_router
from app.modules.tracking.routes import register_ws_routes, router as tracking_router
from app.modules.tracking.simulation import simulation_engine
from app.utils.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongodb.connect()
    await redis_manager.connect()
    await simulation_engine.initialize()
    await simulation_engine.start()
    yield
    await simulation_engine.stop()
    await redis_manager.disconnect()
    await mongodb.disconnect()


def create_app() -> FastAPI:
    setup_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        description="Real-time transit tracking and route query API for BMTC buses in Bengaluru.",
        version=settings.APP_VERSION,
        lifespan=lifespan,
        debug=settings.DEBUG,
    )

    setup_cors(app)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimiterMiddleware)
    register_exception_handlers(app)

    api_prefix = settings.API_PREFIX

    app.include_router(buses_router, prefix=api_prefix)
    app.include_router(routes_router, prefix=api_prefix)
    app.include_router(stops_router, prefix=api_prefix)
    app.include_router(search_router, prefix=api_prefix)
    app.include_router(tracking_router, prefix=api_prefix)
    app.include_router(eta_router, prefix=api_prefix)
    app.include_router(maps_router, prefix=api_prefix)
    app.include_router(analytics_router, prefix=api_prefix)
    app.include_router(notifications_router, prefix=api_prefix)

    register_ws_routes(app)

    @app.get("/")
    async def root():
        return api_response(
            data={"service": settings.APP_NAME, "version": settings.APP_VERSION},
            message="Where is My BMTC API",
        )

    @app.get("/health")
    async def health_check():
        return api_response(
            data={
                "status": "healthy",
                "mongodb": mongodb.db is not None,
                "redis": redis_manager.available,
                "simulation": simulation_engine.running,
            },
            message="Where is My BMTC API is fully functional",
        )

    return app


app = create_app()
