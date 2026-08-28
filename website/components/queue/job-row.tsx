"use client";

import { Download, Play, X } from "lucide-react";

import { ReadoutStrip } from "@/components/readout/readout-strip";
import { StatItem } from "@/components/readout/stat-item";
import { Button } from "@/components/ui/button";
import { useCancelJob } from "@/hooks/use-cancel-job";
import { fileUrl } from "@/lib/api/http-client";
import { isTerminal, type Job } from "@/lib/domain/job";
import { formatFileSize } from "@/lib/format/format-file-size";
import { formatEta, formatSpeed } from "@/lib/format/format-speed";
import { useModal } from "@/providers/modal-provider";

import { JobProgressRule } from "./job-progress-rule";

export function JobRow({ job }: { job: Job }) {
  const { open } = useModal();
  const cancel = useCancelJob();

  const tone =
    job.status === "succeeded"
      ? "done"
      : job.status === "failed"
        ? "fault"
        : job.status === "running" || job.status === "dispatched"
          ? "signal"
          : "idle";

  return (
    <div className="border-border/80 border-b last:border-b-0">
      <ReadoutStrip
        compact
        thumbnail={job.thumbnail_url}
        title={job.title}
        subtitle={job.error?.message ?? statusLine(job)}
        stats={<JobStats job={job} />}
        actions={
          <JobActions
            job={job}
            onCancel={() => cancel.mutate(job.id)}
            onPlay={() => open({ name: "player", job })}
          />
        }
        footer={<JobProgressRule percent={job.progress?.percent ?? 0} tone={tone} />}
      />
    </div>
  );
}

function statusLine(job: Job): string {
  if (job.status === "queued") return "Waiting to start";
  if (job.status === "cancelled") return "Cancelled";
  // The filename is essentially the title again, so show the channel.
  if (job.status === "succeeded") return job.channel || "Ready to save";
  return job.progress?.stage_label ?? "Working";
}

function JobStats({ job }: { job: Job }) {
  if (job.status === "succeeded" && job.result) {
    return (
      <>
        <StatItem label="size" value={formatFileSize(job.result.size_bytes)} />
        <StatItem label="type" value={job.kind === "audio" ? "MP3" : "MP4"} />
      </>
    );
  }
  if (job.status === "running" || job.status === "dispatched") {
    return (
      <>
        <StatItem label="done" value={`${Math.round(job.progress?.percent ?? 0)}%`} />
        <StatItem label="rate" value={formatSpeed(job.progress?.speed_bps)} />
        <StatItem label="eta" value={formatEta(job.progress?.eta_seconds)} />
      </>
    );
  }
  return null;
}

function JobActions({
  job,
  onCancel,
  onPlay,
}: {
  job: Job;
  onCancel: () => void;
  onPlay: () => void;
}) {
  if (job.status === "succeeded" && job.result) {
    return (
      <>
        <Button variant="ghost" size="icon" aria-label="Play" onClick={onPlay}>
          <Play className="size-4" />
        </Button>
        <Button asChild variant="ghost" size="icon" aria-label="Save file">
          <a href={fileUrl(job.result.download_url)} download>
            <Download className="size-4" />
          </a>
        </Button>
      </>
    );
  }

  if (!isTerminal(job.status)) {
    return (
      <Button variant="ghost" size="icon" aria-label="Cancel" onClick={onCancel}>
        <X className="size-4" />
      </Button>
    );
  }
  return null;
}
