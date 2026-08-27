/**
 * Remembers which downloads this tab started, so a refresh does not lose them.
 *
 * Exposed as a subscribable external store rather than component state: it
 * lives in sessionStorage, and useSyncExternalStore is what keeps every reader
 * consistent without setState-in-effect cascades.
 */
const JOBS_KEY = "yetpanda.jobs";
const BATCHES_KEY = "yetpanda.batches";
const MAX_REMEMBERED = 100;

const listeners = new Set<() => void>();

function emit(): void {
  for (const listener of listeners) listener();
}

export function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

function read(key: string): string[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.sessionStorage.getItem(key);
    return raw ? (JSON.parse(raw) as string[]) : [];
  } catch {
    return [];
  }
}

function write(key: string, ids: string[]): void {
  try {
    window.sessionStorage.setItem(key, JSON.stringify(ids.slice(-MAX_REMEMBERED)));
  } catch {
    // A full or blocked sessionStorage must not break the download itself.
  }
  emit();
}

/**
 * Snapshots must be referentially stable or useSyncExternalStore loops
 * forever, so each key caches its last array and replaces it only on change.
 */
const cache = new Map<string, { raw: string; value: string[] }>();
const EMPTY: string[] = [];

function snapshot(key: string): string[] {
  if (typeof window === "undefined") return EMPTY;
  let raw = "[]";
  try {
    raw = window.sessionStorage.getItem(key) ?? "[]";
  } catch {
    return EMPTY;
  }
  const cached = cache.get(key);
  if (cached && cached.raw === raw) return cached.value;
  const value = read(key);
  cache.set(key, { raw, value });
  return value;
}

function makeStore(key: string) {
  return {
    snapshot: () => snapshot(key),
    serverSnapshot: () => EMPTY,
    add: (id: string) => write(key, [...new Set([...read(key), id])]),
    remove: (id: string) => write(key, read(key).filter((value) => value !== id)),
  };
}

export const jobStore = makeStore(JOBS_KEY);
export const batchStore = makeStore(BATCHES_KEY);
