"use client";

import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";

import { createJob, type CreateJobInput } from "@/lib/api/job-api";
import { ApiRequestError } from "@/lib/api/http-client";

export function useCreateJob(onQueued: (jobId: string) => void) {
  return useMutation({
    mutationFn: (input: CreateJobInput) => createJob(input),
    onSuccess: (job) => {
      onQueued(job.id);
      toast.success("Added to downloads");
    },
    onError: (error) => {
      toast.error(
        error instanceof ApiRequestError ? error.message : "Could not start that download.",
      );
    },
  });
}
