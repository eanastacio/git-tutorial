from pydantic import BaseModel


class TopCompanyMetric(BaseModel):
    company_id: int
    company_name: str
    total_filings: int
    certification_rate: float
    sponsorship_score: float


class TrendMetric(BaseModel):
    filing_year: int
    filings: int
    certified: int


class CityMetric(BaseModel):
    city: str
    state: str
    filings: int


class RoleMetric(BaseModel):
    role: str
    filings: int


class DashboardAnalyticsResponse(BaseModel):
    top_companies: list[TopCompanyMetric]
    trends: list[TrendMetric]
    top_cities: list[CityMetric]
    role_breakdown: list[RoleMetric]
