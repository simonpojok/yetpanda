"use client";

import { useMutation } from "@tanstack/react-query";

import { probeUrl } from "@/lib/api/probe-api";
import type { ProbeResult } from "@/lib/domain/probe";

export function useProbe(onResult: (result: ProbeResult) => void) {
  return useMutation({
    mutationFn: (url: string) => probeUrl(url),
    onSuccess: onResult,
  });
}
