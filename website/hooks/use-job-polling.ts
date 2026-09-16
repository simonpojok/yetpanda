"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchJobs } from "@/lib/api/job-api";
import { isTerminal, type Job } from "@/lib/domain/job";

import { usePageVisible } from "./use-page-visible";

const ACTIVE_INTERVAL = 1000;
const QUEUED_INTERVAL = 3000;

/**
 * Polls every watched job in a single request. One request per job would
 * multiply request count by batch size, which is what makes naive
 * implementations fall over on a large playlist.
 */
export function useJobPolling(jobIds: string[]) {
  const visible = usePageVisible();

  return useQuery({
    queryKey: ["jobs", jobIds],
    queryFn: () => fetchJobs(jobIds),
    enabled: jobIds.length > 0,
    refetchInterval: (query) => {
      if (!visible) return false;
      const jobs = (query.state.data ?? []) as Job[];
      if (jobs.length === 0) return ACTIVE_INTERVAL;
      if (jobs.every((job) => isTerminal(job.status))) return false;
      const anyRunning = jobs.some(
        (job) => job.status === "running" || job.status === "dispatched",
      );
      return anyRunning ? ACTIVE_INTERVAL : QUEUED_INTERVAL;
    },
  });
}
