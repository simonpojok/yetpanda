import type { ApiError } from "@/lib/domain/error-code";

/**
 * The API lives on an `api.` subdomain of whatever host serves the page, so
 * the same build works on yetpanda.dev, yetpanda.com and yetpanda.localhost
 * without a rebuild. An explicit env var still wins when the two are split.
 */
function resolveBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (configured) return configured;
  if (typeof window === "undefined") return "";
  const host = window.location.hostname.replace(/^www\./, "");
  return `${window.location.protocol}//api.${host}`;
}

export class ApiRequestError extends Error {
  constructor(readonly apiError: ApiError, readonly status: number) {
    super(apiError.message);
    this.name = "ApiRequestError";
  }
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  signal?: AbortSignal;
}

/**
 * The identity that matters is the server's signed httpOnly cookie, so every
 * request just needs `credentials: "include"`. There is no token to attach.
 */
export async function request<T>(
  path: string,
  { method = "GET", body, signal }: RequestOptions = {},
): Promise<T> {
  const response = await fetch(`${resolveBaseUrl()}${path}`, {
    method,
    credentials: "include",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
    signal,
  });

  if (!response.ok) {
    throw new ApiRequestError(await toApiError(response), response.status);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

async function toApiError(response: Response): Promise<ApiError> {
  try {
    const payload = await response.json();
    if (payload?.error) return payload.error as ApiError;
    // DRF field validation comes back as {field: [messages]}.
    const firstField = Object.values(payload ?? {})[0];
    const message = Array.isArray(firstField) ? String(firstField[0]) : null;
    if (message) {
      return { code: "invalid_url", message, retryable: false };
    }
  } catch {
    // fall through to the generic message
  }
  return {
    code: "unknown",
    message: "Something went wrong. Try again.",
    retryable: true,
  };
}

export function fileUrl(path: string): string {
  return `${resolveBaseUrl()}${path}`;
}
