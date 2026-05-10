from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.core.cache import cache_client
from app.schemas.company import CompanyDetailResponse, CompanyFilters, CompanyListItem, CompanyListResponse
from app.services.company_service import get_company_detail, list_companies, search_companies

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=CompanyListResponse)
async def get_companies(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="score"),
    query: str | None = Query(default=None),
    title: str | None = Query(default=None),
    state: str | None = Query(default=None),
    city: str | None = Query(default=None),
    year: int | None = Query(default=None),
    visa_type: str | None = Query(default=None),
    is_internship: bool | None = Query(default=None),
    is_new_grad: bool | None = Query(default=None),
    min_filings: int | None = Query(default=None),
    max_filings: int | None = Query(default=None),
    remote_type: str | None = Query(default=None),
    session: AsyncSession = Depends(get_db_session),
) -> CompanyListResponse:
    filters = CompanyFilters(
        query=query,
        title=title,
        state=state,
        city=city,
        year=year,
        visa_type=visa_type,
        is_internship=is_internship,
        is_new_grad=is_new_grad,
        min_filings=min_filings,
        max_filings=max_filings,
        remote_type=remote_type,
    )
    cache_key = f"companies:{page}:{page_size}:{sort_by}:{filters.model_dump_json(exclude_none=True)}"
    cached = await cache_client.get_json(cache_key)
    if cached:
        return CompanyListResponse.model_validate(cached)

    response = await list_companies(session, filters=filters, page=page, page_size=page_size, sort_by=sort_by)
    await cache_client.set_json(cache_key, response.model_dump(mode="json"))
    return response


@router.get("/search", response_model=list[CompanyListItem])
async def company_search(
    q: str = Query(min_length=2),
    limit: int = Query(default=10, ge=1, le=50),
    session: AsyncSession = Depends(get_db_session),
) -> list[CompanyListItem]:
    cache_key = f"company-search:{q.lower()}:{limit}"
    cached = await cache_client.get_json(cache_key)
    if cached:
        return [CompanyListItem.model_validate(item) for item in cached]
    results = await search_companies(session, q, limit=limit)
    await cache_client.set_json(cache_key, [item.model_dump(mode="json") for item in results], ttl=120)
    return results


@router.get("/{company_id}", response_model=CompanyDetailResponse)
async def company_detail(company_id: int, session: AsyncSession = Depends(get_db_session)) -> CompanyDetailResponse:
    response = await get_company_detail(session, company_id)
    if not response:
        raise HTTPException(status_code=404, detail="Company not found")
    return response
