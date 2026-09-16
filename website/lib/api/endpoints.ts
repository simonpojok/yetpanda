/** Every API path in one place. No /api prefix - the API lives at /v1/. */
export const endpoints = {
  platforms: "/v1/platforms",
  probe: "/v1/probe",
  jobs: "/v1/jobs",
  job: (id: string) => `/v1/jobs/${id}`,
  jobsByIds: (ids: string[]) => `/v1/jobs?ids=${ids.join(",")}`,
  batches: "/v1/batches",
  batch: (id: string) => `/v1/batches/${id}`,
  batchRetry: (id: string) => `/v1/batches/${id}/retry`,
  batchArchive: (id: string) => `/v1/batches/${id}/archive.zip`,
} as const;
