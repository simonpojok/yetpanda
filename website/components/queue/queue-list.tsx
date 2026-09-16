"use client";

import { Inbox } from "lucide-react";
import { useMemo } from "react";

import { usePagination } from "@/hooks/use-pagination";
import type { Batch } from "@/lib/domain/batch";
import type { Job } from "@/lib/domain/job";

import { BatchRow } from "./batch-row";
import { JobRow } from "./job-row";
import { QueuePagination } from "./queue-pagination";

export const QUEUE_PAGE_SIZE = 5;

type QueueEntry =
  | { kind: "batch"; id: string; createdAt: number; batch: Batch }
  | { kind: "job"; id: string; createdAt: number; job: Job };

/**
 * One newest-first feed of a tab's playlists and single downloads.
 *
 * Batches and jobs come from different endpoints, so interleaving them by age
 * has to happen here rather than being asked of the API.
 */
export function QueueList({
  batches,
  jobs,
  show,
  emptyMessage,
}: {
  batches: Batch[];
  jobs: Job[];
  show: "active" | "finished";
  emptyMessage: string;
}) {
  const entries = useMemo<QueueEntry[]>(() => {
    const merged: QueueEntry[] = [
      ...batches.map((batch) => ({
        kind: "batch" as const,
        id: batch.id,
        createdAt: Date.parse(batch.created_at),
        batch,
      })),
      ...jobs.map((job) => ({
        kind: "job" as const,
        id: job.id,
        createdAt: Date.parse(job.created_at),
        job,
      })),
    ];
    // Newest first. Fall back to id so the order is stable when two downloads
    // are created in the same millisecond, which a playlist can do.
    return merged.sort(
      (a, b) => b.createdAt - a.createdAt || a.id.localeCompare(b.id),
    );
  }, [batches, jobs]);

  const pagination = usePagination(entries, QUEUE_PAGE_SIZE);

  if (entries.length === 0) {
    return <EmptyState message={emptyMessage} />;
  }

  return (
    <>
      {pagination.items.map((entry) =>
        entry.kind === "batch" ? (
          <BatchRow key={entry.id} batchId={entry.id} show={show} />
        ) : (
          <JobRow key={entry.id} job={entry.job} />
        ),
      )}

      {pagination.totalPages > 1 && (
        <QueuePagination
          from={pagination.from}
          to={pagination.to}
          total={pagination.total}
          page={pagination.page}
          totalPages={pagination.totalPages}
          hasPrevious={pagination.hasPrevious}
          hasNext={pagination.hasNext}
          onPrevious={pagination.previous}
          onNext={pagination.next}
        />
      )}
    </>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="text-muted-foreground flex flex-col items-center gap-2 px-4 py-14 text-center">
      <Inbox className="size-5" />
      <p className="text-sm">{message}</p>
    </div>
  );
}