import { CompanyCard } from "@/components/search/company-card";
import { CompanyFilters } from "@/components/search/company-filters";
import { PaginationControls } from "@/components/search/pagination-controls";
import { getCompanies } from "@/lib/api";

type SearchParams = Record<string, string | string[] | undefined>;

function param(searchParams: SearchParams, key: string): string | undefined {
  const value = searchParams[key];
  return Array.isArray(value) ? value[0] : value;
}

export default async function SearchPage({
  searchParams
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await searchParams;
  const page = Number(param(params, "page") ?? "1");
  const pageSize = Number(param(params, "page_size") ?? "20");
  const response = await getCompanies({
    page,
    page_size: pageSize,
    query: param(params, "query"),
    title: param(params, "title"),
    state: param(params, "state"),
    city: param(params, "city"),
    year: param(params, "year"),
    visa_type: param(params, "visa_type"),
    sort_by: param(params, "sort_by") ?? "score"
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Company Search</h1>
        <p className="text-muted-foreground">
          Search by company, role, location, year, visa type, and sponsorship activity.
        </p>
      </div>

      <CompanyFilters />

      <div className="space-y-4">
        {response.data.map((company) => (
          <CompanyCard key={company.id} company={company} />
        ))}
      </div>

      <PaginationControls
        page={response.pagination.page}
        pageSize={response.pagination.page_size}
        total={response.pagination.total}
      />
    </div>
  );
}
