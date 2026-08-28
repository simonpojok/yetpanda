"use client";

import { useQueries } from "@tanstack/react-query";

import { fetchBatch } from "@/lib/api/batch-api";
import { TERMINAL_BATCH_STATUSES, type Batch } from "@/lib/domain/batch";

import { usePageVisible } from "./use-page-visible";

/**
 * Classifies the tab's batches without issuing extra requests: the query key
 * matches the one BatchRow uses, so React Query serves both from one fetch.
 */
export function useBatchList(batchIds: string[]) {
  const visible = usePageVisible();

  const results = useQueries({
    queries: batchIds.map((id) => ({
      queryKey: ["batch", id],
      queryFn: () => fetchBatch(id),
      refetchInterval: (query: { state: { data?: Batch } }) => {
        if (!visible) return false as const;
        const batch = query.state.data;
        if (!batch) return 1000;
        return TERMINAL_BATCH_STATUSES.includes(batch.status) ? (false as const) : 1000;
      },
    })),
  });

  const batches = results
    .map((result) => result.data)
    .filter((batch): batch is Batch => Boolean(batch));

  return {
    active: batches.filter((b) => !TERMINAL_BATCH_STATUSES.includes(b.status)),
    finished: batches.filter((b) => TERMINAL_BATCH_STATUSES.includes(b.status)),
    isLoading: results.some((result) => result.isLoading),
  };
}
