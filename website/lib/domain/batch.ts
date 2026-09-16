import type { Job } from "./job";

export type BatchStatus =
  | "pending"
  | "running"
  | "completed"
  | "completed_with_errors"
  | "failed"
  | "cancelled";

export interface BatchRollup {
  total: number;
  succeeded: number;
  failed: number;
  cancelled: number;
  finished: number;
  percent: number;
  bytes_done: number;
  bytes_total_estimate: number;
}

export interface BatchItem {
  index: number;
  id: string;
  video_id: string;
  title: string;
  duration: number | null;
  status: string;
  size_bytes: number | null;
  download_url?: string;
  error?: { code: string; message: string };
}

export interface BatchArchive {
  available: boolean;
  url: string | null;
  reason: string | null;
}

export interface Batch {
  id: string;
  source_url: string;
  title: string;
  kind: "video" | "audio";
  status: BatchStatus;
  created_at: string;
  completed_at: string | null;
  expires_at: string;
  rollup: BatchRollup;
  active: Job[];
  items: BatchItem[];
  archive: BatchArchive;
}

export const TERMINAL_BATCH_STATUSES: BatchStatus[] = [
  "completed",
  "completed_with_errors",
  "failed",
  "cancelled",
];
