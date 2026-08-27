import type { ApiError } from "./error-code";

export type JobStatus =
  | "queued"
  | "dispatched"
  | "running"
  | "succeeded"
  | "failed"
  | "cancelled"
  | "skipped"
  | "expired";

export const TERMINAL_STATUSES: JobStatus[] = [
  "succeeded",
  "failed",
  "cancelled",
  "skipped",
  "expired",
];

export interface JobProgress {
  stage: string;
  stage_label: string;
  percent: number;
  stage_percent?: number | null;
  downloaded_bytes?: number;
  total_bytes?: number | null;
  speed_bps?: number | null;
  eta_seconds?: number | null;
}

export interface JobResult {
  filename: string;
  content_type: string;
  size_bytes: number;
  expires_at: string;
  stream_url: string;
  download_url: string;
}

export interface Job {
  id: string;
  batch_index: number | null;
  video_id: string;
  title: string;
  channel: string;
  duration: number | null;
  thumbnail_url: string;
  kind: "video" | "audio";
  status: JobStatus;
  created_at: string;
  progress: JobProgress;
  error: ApiError | null;
  result: JobResult | null;
}

export function isTerminal(status: JobStatus): boolean {
  return TERMINAL_STATUSES.includes(status);
}
