import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getTopCompanies } from "@/lib/api";

export default async function LandingPage() {
  const topCompanies = await getTopCompanies(6);

  return (
    <div className="space-y-10">
      <section className="rounded-2xl border border-border bg-gradient-to-br from-blue-600/10 to-indigo-600/5 p-8">
        <h1 className="text-4xl font-bold tracking-tight md:text-5xl">
          Find H1-B Sponsoring Employers with Confidence
        </h1>
        <p className="mt-4 max-w-2xl text-lg text-muted-foreground">
          VisaSponsor helps international students identify internship and full-time opportunities
          using verified Labor Condition Application filings, role trends, and sponsorship scoring.
        </p>
        <div className="mt-6 flex gap-3">
          <Link href="/search">
            <Button size="lg">Explore Companies</Button>
          </Link>
          <Link href="/dashboard">
            <Button size="lg" variant="outline">
              View Analytics
            </Button>
          </Link>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {[
          "Smart search with typo tolerance and filters",
          "Sponsorship scoring based on volume + recency + approvals",
          "Internship/new grad role detection and location trends"
        ].map((feature) => (
          <Card key={feature}>
            <CardHeader>
              <CardTitle className="text-base">{feature}</CardTitle>
            </CardHeader>
          </Card>
        ))}
      </section>

      <section>
        <h2 className="mb-4 text-2xl font-semibold">Top Sponsoring Companies</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {topCompanies.map((company) => (
            <Card key={company.company_id}>
              <CardHeader>
                <CardTitle>{company.company_name}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <p>{company.total_filings.toLocaleString()} filings</p>
                <p>{(company.certification_rate * 100).toFixed(1)}% certification rate</p>
                <p>Sponsorship score: {company.sponsorship_score.toFixed(1)}</p>
                <Link href={`/companies/${company.company_id}`}>
                  <Button variant="outline" size="sm">
                    Open Profile
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
