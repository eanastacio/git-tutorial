export type Pagination = {
  page: number;
  page_size: number;
  total: number;
};

export type Company = {
  id: number;
  normalized_name: string;
  display_name: string;
  total_filings: number;
  total_certified: number;
  sponsorship_score: number;
  latest_filing_year: number | null;
};

export type CompanyListResponse = {
  data: Company[];
  pagination: Pagination;
};

export type CompanyBreakdownItem = {
  label: string;
  filings: number;
};

export type CompanyTrendPoint = {
  filing_year: number;
  total_filings: number;
  certified_filings: number;
};

export type RecentFiling = {
  id: number;
  job_title: string;
  city: string;
  state: string;
  wage: number | null;
  wage_unit: string | null;
  filing_year: number;
  case_status: string;
  visa_class: string;
  filing_date: string | null;
};

export type CompanyDetail = Company & {
  certification_rate: number;
  trends: CompanyTrendPoint[];
  top_titles: CompanyBreakdownItem[];
  top_locations: CompanyBreakdownItem[];
  recent_filings: RecentFiling[];
};

export type TopCompanyMetric = {
  company_id: number;
  company_name: string;
  total_filings: number;
  certification_rate: number;
  sponsorship_score: number;
};

export type TrendMetric = {
  filing_year: number;
  filings: number;
  certified: number;
};

export type CityMetric = {
  city: string;
  state: string;
  filings: number;
};

export type RoleMetric = {
  role: string;
  filings: number;
};

export type DashboardAnalytics = {
  top_companies: TopCompanyMetric[];
  trends: TrendMetric[];
  top_cities: CityMetric[];
  role_breakdown: RoleMetric[];
};

export type SavedCompany = {
  id: number;
  company: Company;
};
