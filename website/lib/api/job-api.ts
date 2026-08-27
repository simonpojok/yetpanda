import { endpoints } from "./endpoints";
import { request } from "./http-client";
import type { Job } from "@/lib/domain/job";
import type { SubtitleMode } from "@/lib/domain/subtitle-track";

export interface CreateJobInput {
  url: string;
  kind: "video" | "audio";
  height?: number;
  audio_bitrate_kbps?: number;
  passthrough?: boolean;
  subtitle_mode?: SubtitleMode;
  subtitle_langs?: string[];
}

export function createJob(input: CreateJobInput): Promise<Job> {
  return request<Job>(endpoints.jobs, { method: "POST", body: input });
}

export function fetchJob(id: string): Promise<Job> {
  return request<Job>(endpoints.job(id));
}

/** One request covers every job being watched, never one request per job. */
export async function fetchJobs(ids: string[]): Promise<Job[]> {
  if (ids.length === 0) return [];
  const data = await request<{ jobs: Job[] }>(endpoints.jobsByIds(ids));
  return data.jobs;
}

export function cancelJob(id: string): Promise<Job> {
  return request<Job>(endpoints.job(id), { method: "DELETE" });
}
