"use client";

import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type Point = {
  filing_year: number;
  filings: number;
  certified?: number;
  total_filings?: number;
  certified_filings?: number;
};

export function FilingsTrendChart({ data }: { data: Point[] }) {
  const normalized = data.map((item) => ({
    year: item.filing_year,
    filings: item.filings ?? item.total_filings ?? 0,
    certified: item.certified ?? item.certified_filings ?? 0
  }));

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={normalized}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="year" />
          <YAxis />
          <Tooltip />
          <Area type="monotone" dataKey="filings" stroke="#2563eb" fill="#93c5fd" />
          <Area type="monotone" dataKey="certified" stroke="#16a34a" fill="#86efac" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
