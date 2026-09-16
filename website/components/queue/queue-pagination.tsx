"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/button";

/**
 * Page controls for a list held in component state.
 *
 * Deliberately not shadcn's `pagination`, which renders anchors with hrefs for
 * URL-driven paging. Nothing here is addressable — it lives inside a modal.
 */
export function QueuePagination({
  from,
  to,
  total,
  page,
  totalPages,
  hasPrevious,
  hasNext,
  onPrevious,
  onNext,
}: {
  from: number;
  to: number;
  total: number;
  page: number;
  totalPages: number;
  hasPrevious: boolean;
  hasNext: boolean;
  onPrevious: () => void;
  onNext: () => void;
}) {
  return (
    <div className="border-border/80 flex items-center justify-between border-t px-4 py-2">
      <p className="tabular text-muted-foreground text-xs">
        {from}&ndash;{to} of {total}
      </p>

      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="icon-sm"
          aria-label="Newer downloads"
          disabled={!hasPrevious}
          onClick={onPrevious}
        >
          <ChevronLeft className="size-4" />
        </Button>
        <span className="tabular text-muted-foreground px-1 text-xs">
          {page} / {totalPages}
        </span>
        <Button
          variant="ghost"
          size="icon-sm"
          aria-label="Older downloads"
          disabled={!hasNext}
          onClick={onNext}
        >
          <ChevronRight className="size-4" />
        </Button>
      </div>
    </div>
  );
}