import { endpoints } from "./endpoints";
import { request } from "./http-client";
import type { ProbeResult } from "@/lib/domain/probe";

export function probeUrl(url: string, signal?: AbortSignal): Promise<ProbeResult> {
  return request<ProbeResult>(endpoints.probe, {
    method: "POST",
    body: { url },
    signal,
  });
}
