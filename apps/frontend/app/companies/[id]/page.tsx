import { notFound } from "next/navigation";

import { BreakdownBarChart } from "@/components/charts/breakdown-bar-chart";
import { FilingsTrendChart } from "@/components/charts/filings-trend-chart";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { getCompany } from "@/lib/api";

export default async function CompanyDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const company = await getCompany(id).catch(() => null);
  if (!company) {
    notFound();
  }
  const certificationRate = (company.certification_rate * 100).toFixed(1);

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-border p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold">{company.display_name}</h1>
            <p className="mt-2 text-muted-foreground">{company.normalized_name}</p>
          </div>
          <Badge className="text-sm">Sponsorship Score: {company.sponsorship_score.toFixed(1)}</Badge>
        </div>
        <div className="mt-4 grid gap-3 text-sm md:grid-cols-4">
          <Card>
            <CardHeader>
              <CardTitle>Total Filings</CardTitle>
            </CardHeader>
            <CardContent>{company.total_filings.toLocaleString()}</CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Total Certified</CardTitle>
            </CardHeader>
            <CardContent>{company.total_certified.toLocaleString()}</CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Certification Rate</CardTitle>
            </CardHeader>
            <CardContent>{certificationRate}%</CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Latest Filing Year</CardTitle>
            </CardHeader>
            <CardContent>{company.latest_filing_year ?? "N/A"}</CardContent>
          </Card>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Filings by Year</CardTitle>
          </CardHeader>
          <CardContent>
            <FilingsTrendChart data={company.trends} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Top Job Titles</CardTitle>
          </CardHeader>
          <CardContent>
            <BreakdownBarChart data={company.top_titles} />
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Top Hiring Locations</CardTitle>
          </CardHeader>
          <CardContent>
            <BreakdownBarChart data={company.top_locations} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Recent Filings</CardTitle>
          </CardHeader>
          <CardContent className="max-h-[420px] overflow-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Year</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Location</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {company.recent_filings.map((filing) => (
                  <TableRow key={filing.id}>
                    <TableCell>{filing.filing_year}</TableCell>
                    <TableCell>{filing.job_title}</TableCell>
                    <TableCell>
                      {filing.city}, {filing.state}
                    </TableCell>
                    <TableCell>{filing.case_status}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
