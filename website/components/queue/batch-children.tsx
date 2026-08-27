"use client";

import { Download } from "lucide-react";

import { Button } from "@/components/ui/button";
import { fileUrl } from "@/lib/api/http-client";
import type { Batch } from "@/lib/domain/batch";
import { formatDuration } from "@/lib/format/format-duration";
import { cn } from "@/lib/utils";

export function BatchChildren({ batch }: { batch: Batch }) {
  return (
    <ul className="bg-muted/40 divide-border/60 divide-y">
      {batch.items.map((item) => (
        <li key={item.id} className="flex items-center gap-3 px-4 py-2">
          <span className="tabular text-muted-foreground w-6 shrink-0 text-right text-xs">
            {item.index + 1}
          </span>
          <span className="min-w-0 flex-1 truncate text-xs" title={item.title}>
            {item.title}
          </span>
          <span className="tabular text-muted-foreground shrink-0 text-xs">
            {formatDuration(item.duration)}
          </span>
          <span
            className={cn(
              "w-16 shrink-0 text-right text-[11px]",
              item.status === "succeeded" && "text-done",
              item.status === "failed" && "text-fault",
              item.status !== "succeeded" && item.status !== "failed" && "text-muted-foreground",
            )}
            title={item.error?.message}
          >
            {item.status}
          </span>
          {item.download_url ? (
            <Button asChild variant="ghost" size="icon" className="size-7 shrink-0" aria-label="Save file">
              <a href={fileUrl(item.download_url)} download>
                <Download className="size-3.5" />
              </a>
            </Button>
          ) : (
            <span className="w-7 shrink-0" />
          )}
        </li>
      ))}
    </ul>
  );
}
