"use client";

import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";

import { createBatch, type CreateBatchInput } from "@/lib/api/batch-api";
import { ApiRequestError } from "@/lib/api/http-client";

export function useCreateBatch(onQueued: (batchId: string) => void) {
  return useMutation({
    mutationFn: (input: CreateBatchInput) => createBatch(input),
    onSuccess: (batch) => {
      onQueued(batch.id);
      toast.success(`Added ${batch.rollup.total} items to downloads`);
    },
    onError: (error) => {
      toast.error(
        error instanceof ApiRequestError ? error.message : "Could not start that playlist.",
      );
    },
  });
}
