"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuth, useClerk } from "@clerk/nextjs";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { deleteSavedCompany, getSavedCompanies } from "@/lib/api";
import { SavedCompany } from "@/types/api";

export function SavedCompaniesList() {
  const { userId, getToken } = useAuth();
  const clerk = useClerk();
  const [items, setItems] = useState<SavedCompany[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const run = async () => {
      if (!userId) {
        setLoading(false);
        return;
      }
      const token = await getToken();
      if (!token) {
        setLoading(false);
        return;
      }
      const saved = await getSavedCompanies(token);
      setItems(saved);
      setLoading(false);
    };
    run();
  }, [userId, getToken]);

  const remove = async (companyId: number) => {
    const token = await getToken();
    if (!token) return;
    await deleteSavedCompany(token, companyId);
    setItems((prev) => prev.filter((entry) => entry.company.id !== companyId));
  };

  if (!userId) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Sign in to view saved companies</CardTitle>
        </CardHeader>
        <CardContent>
          <Button onClick={() => clerk.openSignIn()}>Sign In</Button>
        </CardContent>
      </Card>
    );
  }

  if (loading) {
    return <p className="text-sm text-muted-foreground">Loading saved companies...</p>;
  }

  if (items.length === 0) {
    return <p className="text-sm text-muted-foreground">No saved companies yet.</p>;
  }

  return (
    <div className="space-y-3">
      {items.map((item) => (
        <Card key={item.id}>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>{item.company.display_name}</CardTitle>
            <p className="text-sm text-muted-foreground">
              Score {item.company.sponsorship_score.toFixed(1)}
            </p>
          </CardHeader>
          <CardContent className="flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              {item.company.total_filings.toLocaleString()} filings
            </div>
            <div className="flex gap-2">
              <Link href={`/companies/${item.company.id}`}>
                <Button variant="outline">Open</Button>
              </Link>
              <Button variant="ghost" onClick={() => remove(item.company.id)}>
                Remove
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
