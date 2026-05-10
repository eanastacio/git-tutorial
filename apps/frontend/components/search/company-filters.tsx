"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { searchCompanies } from "@/lib/api";

export function CompanyFilters() {
  const params = useSearchParams();
  const router = useRouter();
  const [company, setCompany] = useState(params.get("query") ?? "");
  const [title, setTitle] = useState(params.get("title") ?? "");
  const [state, setState] = useState(params.get("state") ?? "");
  const [year, setYear] = useState(params.get("year") ?? "");
  const [suggestions, setSuggestions] = useState<string[]>([]);

  useEffect(() => {
    const run = async () => {
      if (company.length < 2) {
        setSuggestions([]);
        return;
      }
      const response = await searchCompanies(company);
      setSuggestions(response.map((item) => item.display_name));
    };
    const timeout = setTimeout(run, 180);
    return () => clearTimeout(timeout);
  }, [company]);

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    const next = new URLSearchParams(params.toString());
    if (company) next.set("query", company);
    else next.delete("query");
    if (title) next.set("title", title);
    else next.delete("title");
    if (state) next.set("state", state.toUpperCase());
    else next.delete("state");
    if (year) next.set("year", year);
    else next.delete("year");
    next.set("page", "1");
    router.push(`/search?${next.toString()}`);
  };

  return (
    <form onSubmit={onSubmit} className="grid gap-3 rounded-xl border border-border p-4 md:grid-cols-5">
      <div>
        <Input
          placeholder="Company name"
          value={company}
          onChange={(e) => setCompany(e.target.value)}
          list="company-suggestions"
        />
        <datalist id="company-suggestions">
          {suggestions.map((name) => (
            <option key={name} value={name} />
          ))}
        </datalist>
      </div>
      <Input placeholder="Role or title" value={title} onChange={(e) => setTitle(e.target.value)} />
      <Input
        placeholder="State (CA)"
        maxLength={2}
        value={state}
        onChange={(e) => setState(e.target.value)}
      />
      <Input
        placeholder="Year (2025)"
        value={year}
        onChange={(e) => setYear(e.target.value.replace(/\D/g, ""))}
      />
      <Button type="submit">Apply Filters</Button>
    </form>
  );
}
