import { API_BASE_URL } from "@/lib/utils";
import {
  CompanyDetail,
  CompanyListResponse,
  DashboardAnalytics,
  SavedCompany,
  TopCompanyMetric,
  TrendMetric
} from "@/types/api";

type QueryParams = Record<string, string | number | boolean | undefined | null>;

function toQueryString(params: QueryParams) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") {
      return;
    }
    search.append(key, String(value));
  });
  return search.toString();
}

async function parseJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || `Request failed with status ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function getCompanies(filters: QueryParams): Promise<CompanyListResponse> {
  const qs = toQueryString(filters);
  const res = await fetch(`${API_BASE_URL}/companies?${qs}`, { cache: "no-store" });
  return parseJson<CompanyListResponse>(res);
}

export async function searchCompanies(query: string): Promise<CompanyListResponse["data"]> {
  const qs = toQueryString({ q: query });
  const res = await fetch(`${API_BASE_URL}/companies/search?${qs}`, { cache: "no-store" });
  return parseJson<CompanyListResponse["data"]>(res);
}

export async function getCompany(companyId: string | number): Promise<CompanyDetail> {
  const res = await fetch(`${API_BASE_URL}/companies/${companyId}`, { cache: "no-store" });
  return parseJson<CompanyDetail>(res);
}

export async function getDashboardAnalytics(): Promise<DashboardAnalytics> {
  const res = await fetch(`${API_BASE_URL}/analytics/dashboard`, { cache: "no-store" });
  return parseJson<DashboardAnalytics>(res);
}

export async function getTopCompanies(limit = 10): Promise<TopCompanyMetric[]> {
  const res = await fetch(`${API_BASE_URL}/analytics/top-companies?limit=${limit}`, { cache: "no-store" });
  return parseJson<TopCompanyMetric[]>(res);
}

export async function getTrends(): Promise<TrendMetric[]> {
  const res = await fetch(`${API_BASE_URL}/analytics/trends`, { cache: "no-store" });
  return parseJson<TrendMetric[]>(res);
}

export async function getSavedCompanies(token: string): Promise<SavedCompany[]> {
  const res = await fetch(`${API_BASE_URL}/saved-companies`, {
    headers: {
      Authorization: `Bearer ${token}`
    },
    cache: "no-store"
  });
  return parseJson<SavedCompany[]>(res);
}

export async function saveCompany(token: string, companyId: number): Promise<SavedCompany> {
  const res = await fetch(`${API_BASE_URL}/saved-companies`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ company_id: companyId })
  });
  return parseJson<SavedCompany>(res);
}

export async function deleteSavedCompany(token: string, companyId: number): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/saved-companies/${companyId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  if (!res.ok && res.status !== 204) {
    throw new Error(await res.text());
  }
}
