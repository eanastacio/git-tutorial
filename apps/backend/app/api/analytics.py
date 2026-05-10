from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.core.cache import cache_client
from app.schemas.analytics import DashboardAnalyticsResponse, TopCompanyMetric, TrendMetric
from app.services.analytics_service import dashboard_analytics, filings_trends, top_companies

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/top-companies", response_model=list[TopCompanyMetric])
async def get_top_companies(
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
) -> list[TopCompanyMetric]:
    cache_key = f"analytics:top-companies:{limit}"
    cached = await cache_client.get_json(cache_key)
    if cached:
        return [TopCompanyMetric.model_validate(item) for item in cached]
    response = await top_companies(session, limit=limit)
    await cache_client.set_json(cache_key, [item.model_dump(mode="json") for item in response], ttl=300)
    return response


@router.get("/trends", response_model=list[TrendMetric])
async def get_trends(
    visa_type: str | None = Query(default=None),
    session: AsyncSession = Depends(get_db_session),
) -> list[TrendMetric]:
    cache_key = f"analytics:trends:{visa_type or 'all'}"
    cached = await cache_client.get_json(cache_key)
    if cached:
        return [TrendMetric.model_validate(item) for item in cached]
    response = await filings_trends(session, visa_type=visa_type)
    await cache_client.set_json(cache_key, [item.model_dump(mode="json") for item in response], ttl=300)
    return response


@router.get("/dashboard", response_model=DashboardAnalyticsResponse)
async def get_dashboard(session: AsyncSession = Depends(get_db_session)) -> DashboardAnalyticsResponse:
    cache_key = "analytics:dashboard"
    cached = await cache_client.get_json(cache_key)
    if cached:
        return DashboardAnalyticsResponse.model_validate(cached)
    response = await dashboard_analytics(session)
    await cache_client.set_json(cache_key, response.model_dump(mode="json"), ttl=300)
    return response
