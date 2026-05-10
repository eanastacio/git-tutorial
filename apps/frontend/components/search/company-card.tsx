"use client";

import Link from "next/link";
import { useState } from "react";
import { useAuth, useClerk } from "@clerk/nextjs";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { saveCompany } from "@/lib/api";
import { Company } from "@/types/api";

export function CompanyCard({ company }: { company: Company }) {
  const { getToken, userId } = useAuth();
  const clerk = useClerk();
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const onSave = async () => {
    if (!userId) {
      clerk.openSignIn();
      return;
    }
    const token = await getToken();
    if (!token) return;
    setSaving(true);
    try {
      await saveCompany(token, company.id);
      setSaved(true);
    } finally {
      setSaving(false);
    }
  };

  const certificationRate =
    company.total_filings > 0 ? ((company.total_certified / company.total_filings) * 100).toFixed(1) : "0.0";

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>{company.display_name}</CardTitle>
          <p className="mt-1 text-sm text-muted-foreground">
            {company.total_filings.toLocaleString()} filings • {certificationRate}% certified
          </p>
        </div>
        <Badge>Sponsorship Score: {company.sponsorship_score.toFixed(1)}</Badge>
      </CardHeader>
      <CardContent className="flex flex-wrap items-center justify-between gap-3">
        <div className="text-sm text-muted-foreground">
          Latest activity: {company.latest_filing_year ?? "N/A"}
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={onSave} disabled={saving || saved}>
            {saved ? "Saved" : saving ? "Saving..." : "Save"}
          </Button>
          <Link href={`/companies/${company.id}`}>
            <Button>View Details</Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
