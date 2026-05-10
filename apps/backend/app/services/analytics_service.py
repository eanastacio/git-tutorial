from __future__ import annotations

from decimal import Decimal

from sqlalchemy import case, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Company, LCARecord
from app.schemas.analytics import (
    CityMetric,
    DashboardAnalyticsResponse,
    RoleMetric,
    TopCompanyMetric,
    TrendMetric,
)


def _as_float(value: Decimal | float | None) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return value


async def top_companies(session: AsyncSession, limit: int = 20) -> list[TopCompanyMetric]:
    companies = (
        await session.execute(
            select(Company).order_by(desc(Company.sponsorship_score), desc(Company.total_filings)).limit(limit)
        )
    ).scalars().all()
    response = []
    for company in companies:
        certification_rate = company.total_certified / company.total_filings if company.total_filings else 0
        response.append(
            TopCompanyMetric(
                company_id=company.id,
                company_name=company.display_name,
                total_filings=company.total_filings,
                certification_rate=round(certification_rate, 4),
                sponsorship_score=_as_float(company.sponsorship_score),
            )
        )
    return response


async def filings_trends(session: AsyncSession, visa_type: str | None = None) -> list[TrendMetric]:
    query = select(
        LCARecord.filing_year,
        func.count(LCARecord.id),
        func.sum(case((LCARecord.case_status.like("CERTIFIED%"), 1), else_=0)),
    ).group_by(LCARecord.filing_year).order_by(LCARecord.filing_year)
    if visa_type:
        query = query.where(LCARecord.visa_class == visa_type.upper())

    trends = (await session.execute(query)).all()
    return [
        TrendMetric(filing_year=filing_year, filings=filings, certified=certified or 0)
        for filing_year, filings, certified in trends
    ]


async def top_cities(session: AsyncSession, limit: int = 15) -> list[CityMetric]:
    rows = (
        await session.execute(
            select(LCARecord.city, LCARecord.state, func.count(LCARecord.id).label("total"))
            .group_by(LCARecord.city, LCARecord.state)
            .order_by(desc("total"))
            .limit(limit)
        )
    ).all()
    return [CityMetric(city=city, state=state, filings=filings) for city, state, filings in rows]


async def role_breakdown(session: AsyncSession, limit: int = 15) -> list[RoleMetric]:
    rows = (
        await session.execute(
            select(LCARecord.job_title, func.count(LCARecord.id).label("total"))
            .group_by(LCARecord.job_title)
            .order_by(desc("total"))
            .limit(limit)
        )
    ).all()
    return [RoleMetric(role=role, filings=filings) for role, filings in rows]


async def dashboard_analytics(session: AsyncSession) -> DashboardAnalyticsResponse:
    return DashboardAnalyticsResponse(
        top_companies=await top_companies(session),
        trends=await filings_trends(session),
        top_cities=await top_cities(session),
        role_breakdown=await role_breakdown(session),
    )
