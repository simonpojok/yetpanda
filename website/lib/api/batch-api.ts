import { endpoints } from "./endpoints";
import { request } from "./http-client";
import type { Batch } from "@/lib/domain/batch";
import type { CreateJobInput } from "./job-api";

export interface CreateBatchInput extends CreateJobInput {
  item_indexes?: number[];
}

export function createBatch(input: CreateBatchInput): Promise<Batch> {
  return request<Batch>(endpoints.batches, { method: "POST", body: input });
}

export function fetchBatch(id: string): Promise<Batch> {
  return request<Batch>(endpoints.batch(id));
}

export function cancelBatch(id: string): Promise<Batch> {
  return request<Batch>(endpoints.batch(id), { method: "DELETE" });
}

export function retryBatch(id: string): Promise<{ retrying: number; skipped: number }> {
  return request(endpoints.batchRetry(id), { method: "POST" });
}
