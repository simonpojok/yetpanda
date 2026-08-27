"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchBatch } from "@/lib/api/batch-api";
import { TERMINAL_BATCH_STATUSES, type Batch } from "@/lib/domain/batch";

import { usePageVisible } from "./use-page-visible";

export function useBatchPolling(batchId: string | null) {
  const visible = usePageVisible();

  return useQuery({
    queryKey: ["batch", batchId],
    queryFn: () => fetchBatch(batchId as string),
    enabled: Boolean(batchId),
    refetchInterval: (query) => {
      if (!visible) return false;
      const batch = query.state.data as Batch | undefined;
      if (!batch) return 1000;
      return TERMINAL_BATCH_STATUSES.includes(batch.status) ? false : 1000;
    },
  });
}
