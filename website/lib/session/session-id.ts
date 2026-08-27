/**
 * A per-tab id for the session-only library.
 *
 * This is purely a client-side key: quotas and authorisation run off the
 * server's signed httpOnly cookie, which page scripts cannot reach or rotate.
 */
const STORAGE_KEY = "yetpanda.session";

export function getSessionId(): string {
  if (typeof window === "undefined") return "";
  const existing = window.sessionStorage.getItem(STORAGE_KEY);
  if (existing) return existing;
  const id = crypto.randomUUID();
  window.sessionStorage.setItem(STORAGE_KEY, id);
  return id;
}
