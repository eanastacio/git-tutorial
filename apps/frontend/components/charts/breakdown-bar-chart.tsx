"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type BreakdownData = {
  label: string;
  filings: number;
};

export function BreakdownBarChart({ data }: { data: BreakdownData[] }) {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="label" interval={0} angle={-20} height={70} textAnchor="end" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="filings" fill="#4f46e5" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
