"use client";

import { useCallback, useSyncExternalStore } from "react";

import { batchStore, jobStore, subscribe } from "@/lib/session/job-store";

/** Tracks what this tab started. Cleared when the tab closes, by design. */
export function useDownloadSession() {
  const jobIds = useSyncExternalStore(
    subscribe,
    jobStore.snapshot,
    jobStore.serverSnapshot,
  );
  const batchIds = useSyncExternalStore(
    subscribe,
    batchStore.snapshot,
    batchStore.serverSnapshot,
  );

  const addJob = useCallback((id: string) => jobStore.add(id), []);
  const addBatch = useCallback((id: string) => batchStore.add(id), []);
  const removeJob = useCallback((id: string) => jobStore.remove(id), []);
  const removeBatch = useCallback((id: string) => batchStore.remove(id), []);

  return { jobIds, batchIds, addJob, addBatch, removeJob, removeBatch };
}
