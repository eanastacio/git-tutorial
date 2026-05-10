from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase, Pagination


class CompanyListItem(ORMBase):
    id: int
    normalized_name: str
    display_name: str
    total_filings: int
    total_certified: int
    sponsorship_score: float
    latest_filing_year: int | None = None


class CompanyListResponse(BaseModel):
    data: list[CompanyListItem]
    pagination: Pagination


class CompanyTrendPoint(BaseModel):
    filing_year: int
    total_filings: int
    certified_filings: int


class CompanyBreakdownItem(BaseModel):
    label: str
    filings: int


class RecentFilingItem(BaseModel):
    id: int
    job_title: str
    city: str
    state: str
    wage: float | None
    wage_unit: str | None
    filing_year: int
    case_status: str
    visa_class: str
    filing_date: str | None


class CompanyDetailResponse(CompanyListItem):
    certification_rate: float
    trends: list[CompanyTrendPoint]
    top_titles: list[CompanyBreakdownItem]
    top_locations: list[CompanyBreakdownItem]
    recent_filings: list[RecentFilingItem]


class CompanyFilters(BaseModel):
    query: str | None = None
    title: str | None = None
    state: str | None = Field(default=None, min_length=2, max_length=2)
    city: str | None = None
    year: int | None = None
    visa_type: str | None = None
    is_internship: bool | None = None
    is_new_grad: bool | None = None
    min_filings: int | None = None
    max_filings: int | None = None
    remote_type: Literal["on-site", "hybrid", "remote"] | None = None
