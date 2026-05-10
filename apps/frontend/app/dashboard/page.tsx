import { BreakdownBarChart } from "@/components/charts/breakdown-bar-chart";
import { FilingsTrendChart } from "@/components/charts/filings-trend-chart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getDashboardAnalytics } from "@/lib/api";

export default async function DashboardPage() {
  const analytics = await getDashboardAnalytics();

  const topCities = analytics.top_cities.map((city) => ({
    label: `${city.city}, ${city.state}`,
    filings: city.filings
  }));
  const topRoles = analytics.role_breakdown.map((role) => ({ label: role.role, filings: role.filings }));

  return (
    <div className="space-y-6">
      <section>
        <h1 className="text-3xl font-bold">Sponsorship Analytics Dashboard</h1>
        <p className="text-muted-foreground">
          Explore historical filing trends, top sponsoring companies, and role/location insights.
        </p>
      </section>

      <Card>
        <CardHeader>
          <CardTitle>National Filing Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <FilingsTrendChart data={analytics.trends} />
        </CardContent>
      </Card>

      <section className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Top Sponsorship Cities</CardTitle>
          </CardHeader>
          <CardContent>
            <BreakdownBarChart data={topCities} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Top Sponsored Roles</CardTitle>
          </CardHeader>
          <CardContent>
            <BreakdownBarChart data={topRoles} />
          </CardContent>
        </Card>
      </section>

      <Card>
        <CardHeader>
          <CardTitle>Top Sponsoring Companies</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {analytics.top_companies.map((company) => (
              <div key={company.company_id} className="rounded-lg border border-border p-4">
                <p className="font-semibold">{company.company_name}</p>
                <p className="text-sm text-muted-foreground">
                  {company.total_filings.toLocaleString()} filings
                </p>
                <p className="text-sm text-muted-foreground">
                  {(company.certification_rate * 100).toFixed(1)}% certified
                </p>
                <p className="mt-1 text-sm font-medium">
                  Score: {company.sponsorship_score.toFixed(1)}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
