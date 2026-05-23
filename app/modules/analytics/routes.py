"""Analytics API routes."""

from fastapi import APIRouter

from app.modules.analytics.controller import AnalyticsController

router = APIRouter(prefix="/analytics", tags=["analytics"])
controller = AnalyticsController()


@router.get("/popular-routes")
async def popular_routes():
    return await controller.popular_routes()


@router.get("/popular-searches")
async def popular_searches():
    return await controller.popular_searches()
