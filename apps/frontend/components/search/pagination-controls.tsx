"use client";

import { useRouter, useSearchParams } from "next/navigation";

import { Button } from "@/components/ui/button";

type Props = {
  page: number;
  pageSize: number;
  total: number;
};

export function PaginationControls({ page, pageSize, total }: Props) {
  const router = useRouter();
  const params = useSearchParams();
  const totalPages = Math.max(Math.ceil(total / pageSize), 1);

  const updatePage = (nextPage: number) => {
    const next = new URLSearchParams(params.toString());
    next.set("page", String(nextPage));
    router.push(`/search?${next.toString()}`);
  };

  return (
    <div className="flex items-center justify-between">
      <p className="text-sm text-muted-foreground">
        Page {page} of {totalPages} ({total.toLocaleString()} companies)
      </p>
      <div className="flex gap-2">
        <Button variant="outline" onClick={() => updatePage(page - 1)} disabled={page <= 1}>
          Previous
        </Button>
        <Button onClick={() => updatePage(page + 1)} disabled={page >= totalPages}>
          Next
        </Button>
      </div>
    </div>
  );
}
