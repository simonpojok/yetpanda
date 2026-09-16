/** Error codes the API can return. Mirrors apps/extraction/domain/error_code.py. */
export type ErrorCode =
  | "invalid_url"
  | "unsupported_host"
  | "not_found"
  | "private"
  | "members_only"
  | "age_restricted"
  | "geo_blocked"
  | "live_not_supported"
  | "drm_protected"
  | "too_long"
  | "too_large"
  | "quota_exceeded"
  | "cancelled"
  | "bot_check"
  | "throttled"
  | "network"
  | "extractor_error"
  | "postprocess_failed"
  | "disk_full"
  | "worker_lost"
  | "unknown";

export interface ApiError {
  code: ErrorCode;
  message: string;
  retryable: boolean;
}
