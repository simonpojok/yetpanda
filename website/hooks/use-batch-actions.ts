"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { cancelBatch, retryBatch } from "@/lib/api/batch-api";

export function useRetryBatch(batchId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => retryBatch(batchId),
    onSuccess: ({ retrying, skipped }) => {
      queryClient.invalidateQueries({ queryKey: ["batch", batchId] });
      if (retrying === 0) {
        toast("Those items cannot be retried.");
        return;
      }
      // Some failures never succeed on a second attempt, so say so rather
      // than implying everything is being retried.
      toast.success(
        skipped > 0
          ? `Retrying ${retrying}, ${skipped} cannot be retried`
          : `Retrying ${retrying} ${retrying === 1 ? "item" : "items"}`,
      );
    },
    onError: () => toast.error("Could not retry those items."),
  });
}

export function useCancelBatch(batchId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => cancelBatch(batchId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["batch", batchId] });
      toast("Playlist cancelled");
    },
  });
}
