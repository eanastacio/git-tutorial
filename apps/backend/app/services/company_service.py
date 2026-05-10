from __future__ import annotations

from decimal import Decimal
from typing import Any

from rapidfuzz import fuzz
from sqlalchemy import and_, case, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Company, LCARecord
from app.schemas.company import (
    CompanyBreakdownItem,
    CompanyDetailResponse,
    CompanyFilters,
    CompanyListItem,
    CompanyListResponse,
    CompanyTrendPoint,
    RecentFilingItem,
)
from app.schemas.common import Pagination


def _as_float(value: Decimal | float | None) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return value


async def list_companies(
    session: AsyncSession,
    filters: CompanyFilters,
    page: int,
    page_size: int,
    sort_by: str,
) -> CompanyListResponse:
    where_clauses: list[Any] = []
    lca_filters: list[Any] = []

    if filters.query:
        term = f"%{filters.query.lower()}%"
        where_clauses.append(or_(func.lower(Company.display_name).like(term), Company.normalized_name.like(term)))
    if filters.title:
        lca_filters.append(func.lower(LCARecord.job_title).like(f"%{filters.title.lower()}%"))
    if filters.state:
        lca_filters.append(LCARecord.state == filters.state.upper())
    if filters.city:
        lca_filters.append(func.lower(LCARecord.city) == filters.city.lower())
    if filters.year:
        lca_filters.append(LCARecord.filing_year == filters.year)
    if filters.visa_type:
        lca_filters.append(LCARecord.visa_class == filters.visa_type.upper())
    if filters.is_internship is not None:
        lca_filters.append(LCARecord.is_internship_role == filters.is_internship)
    if filters.is_new_grad is not None:
        lca_filters.append(LCARecord.is_new_grad_role == filters.is_new_grad)
    if filters.remote_type:
        lca_filters.append(LCARecord.remote_type == filters.remote_type)
    if filters.min_filings is not None:
        where_clauses.append(Company.total_filings >= filters.min_filings)
    if filters.max_filings is not None:
        where_clauses.append(Company.total_filings <= filters.max_filings)

    query = select(Company)

    if lca_filters:
        query = (
            query.join(LCARecord, LCARecord.company_id == Company.id)
            .where(and_(*lca_filters))
            .group_by(Company.id)
        )

    if where_clauses:
        query = query.where(and_(*where_clauses))

    if sort_by == "filings":
        query = query.order_by(desc(Company.total_filings), desc(Company.sponsorship_score))
    elif sort_by == "recent":
        query = query.order_by(desc(Company.latest_filing_year), desc(Company.total_filings))
    else:
        query = query.order_by(desc(Company.sponsorship_score), desc(Company.total_filings))

    count_query = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_query)).scalar_one()

    offset = (page - 1) * page_size
    companies = (await session.execute(query.offset(offset).limit(page_size))).scalars().all()

    data = [
        CompanyListItem(
            id=company.id,
            normalized_name=company.normalized_name,
            display_name=company.display_name,
            total_filings=company.total_filings,
            total_certified=company.total_certified,
            sponsorship_score=_as_float(company.sponsorship_score),
            latest_filing_year=company.latest_filing_year,
        )
        for company in companies
    ]
    return CompanyListResponse(data=data, pagination=Pagination(page=page, page_size=page_size, total=total))


async def search_companies(session: AsyncSession, query: str, limit: int = 10) -> list[CompanyListItem]:
    lowered = query.lower().strip()
    term = f"%{lowered}%"
    results = (
        await session.execute(
            select(Company)
            .where(or_(func.lower(Company.display_name).like(term), Company.normalized_name.like(term)))
            .order_by(desc(Company.total_filings))
            .limit(100)
        )
    ).scalars().all()

    ranked = sorted(
        results,
        key=lambda company: (
            fuzz.token_set_ratio(lowered, company.display_name.lower()),
            company.total_filings,
        ),
        reverse=True,
    )[:limit]

    return [
        CompanyListItem(
            id=company.id,
            normalized_name=company.normalized_name,
            display_name=company.display_name,
            total_filings=company.total_filings,
            total_certified=company.total_certified,
            sponsorship_score=_as_float(company.sponsorship_score),
            latest_filing_year=company.latest_filing_year,
        )
        for company in ranked
    ]


async def get_company_detail(session: AsyncSession, company_id: int) -> CompanyDetailResponse | None:
    company = (await session.execute(select(Company).where(Company.id == company_id))).scalar_one_or_none()
    if not company:
        return None

    trends = (
        await session.execute(
            select(
                LCARecord.filing_year,
                func.count(LCARecord.id),
                func.sum(case((LCARecord.case_status.like("CERTIFIED%"), 1), else_=0)),
            )
            .where(LCARecord.company_id == company_id)
            .group_by(LCARecord.filing_year)
            .order_by(LCARecord.filing_year)
        )
    ).all()

    top_titles = (
        await session.execute(
            select(LCARecord.job_title, func.count(LCARecord.id).label("total"))
            .where(LCARecord.company_id == company_id)
            .group_by(LCARecord.job_title)
            .order_by(desc("total"))
            .limit(8)
        )
    ).all()

    top_locations = (
        await session.execute(
            select(func.concat(LCARecord.city, ", ", LCARecord.state).label("location"), func.count(LCARecord.id).label("total"))
            .where(LCARecord.company_id == company_id)
            .group_by(LCARecord.city, LCARecord.state)
            .order_by(desc("total"))
            .limit(8)
        )
    ).all()

    recent_filings = (
        await session.execute(
            select(LCARecord)
            .where(LCARecord.company_id == company_id)
            .order_by(desc(LCARecord.filing_year), desc(LCARecord.id))
            .limit(25)
        )
    ).scalars().all()

    certification_rate = company.total_certified / company.total_filings if company.total_filings else 0
    trend_points = [
        CompanyTrendPoint(
            filing_year=year,
            total_filings=total,
            certified_filings=certified or 0,
        )
        for year, total, certified in trends
    ]

    return CompanyDetailResponse(
        id=company.id,
        normalized_name=company.normalized_name,
        display_name=company.display_name,
        total_filings=company.total_filings,
        total_certified=company.total_certified,
        sponsorship_score=_as_float(company.sponsorship_score),
        latest_filing_year=company.latest_filing_year,
        certification_rate=round(certification_rate, 4),
        trends=trend_points,
        top_titles=[CompanyBreakdownItem(label=label, filings=total) for label, total in top_titles],
        top_locations=[CompanyBreakdownItem(label=label, filings=total) for label, total in top_locations],
        recent_filings=[
            RecentFilingItem(
                id=item.id,
                job_title=item.job_title,
                city=item.city,
                state=item.state,
                wage=_as_float(item.wage),
                wage_unit=item.wage_unit,
                filing_year=item.filing_year,
                case_status=item.case_status,
                visa_class=item.visa_class,
                filing_date=item.filing_date.isoformat() if item.filing_date else None,
            )
            for item in recent_filings
        ],
    )
