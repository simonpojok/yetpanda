"use client";

import { ChevronDown, ChevronRight, FileArchive } from "lucide-react";
import { useState } from "react";

import { StatItem } from "@/components/readout/stat-item";
import { Button } from "@/components/ui/button";
import { useBatchPolling } from "@/hooks/use-batch-polling";
import { fileUrl } from "@/lib/api/http-client";
import { formatFileSize } from "@/lib/format/format-file-size";

import { BatchChildren } from "./batch-children";
import { JobProgressRule } from "./job-progress-rule";

export function BatchRow({ batchId }: { batchId: string }) {
  const [expanded, setExpanded] = useState(false);
  const { data: batch } = useBatchPolling(batchId);

  if (!batch) return null;

  const { rollup, archive } = batch;
  const tone =
    batch.status === "completed"
      ? "done"
      : batch.status === "failed"
        ? "fault"
        : batch.status === "running" || batch.status === "pending"
          ? "signal"
          : "idle";

  return (
    <div className="border-border/80 border-b last:border-b-0">
      <div className="flex items-start gap-2 p-3 sm:p-4">
        <Button
          variant="ghost"
          size="icon"
          className="mt-0.5 size-6 shrink-0"
          aria-label={expanded ? "Hide items" : "Show items"}
          onClick={() => setExpanded((value) => !value)}
        >
          {expanded ? (
            <ChevronDown className="size-4" />
          ) : (
            <ChevronRight className="size-4" />
          )}
        </Button>

        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium" title={batch.title}>
            {batch.title}
          </p>
          <p className="text-muted-foreground mt-0.5 text-xs">
            {describe(batch.status)}
          </p>

          <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1">
            <StatItem
              label="done"
              value={`${rollup.succeeded} of ${rollup.total}`}
            />
            {rollup.failed > 0 && (
              <StatItem label="failed" value={String(rollup.failed)} />
            )}
            <StatItem label="size" value={formatFileSize(rollup.bytes_done)} />
          </div>
        </div>

        {archive.available && archive.url && (
          <Button asChild variant="outline" size="sm" className="shrink-0 gap-2">
            <a href={fileUrl(archive.url)} download>
              <FileArchive className="size-4" />
              ZIP
            </a>
          </Button>
        )}
      </div>

      <JobProgressRule percent={rollup.percent} tone={tone} />

      {expanded && <BatchChildren batch={batch} />}
    </div>
  );
}

function describe(status: string): string {
  switch (status) {
    case "pending":
      return "Waiting to start";
    case "running":
      return "Downloading";
    case "completed":
      return "All items downloaded";
    case "completed_with_errors":
      return "Finished, some items failed";
    case "failed":
      return "Nothing downloaded";
    case "cancelled":
      return "Cancelled";
    default:
      return status;
  }
}
