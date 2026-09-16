import { formatFileSize } from "./format-file-size";

export function formatSpeed(bytesPerSecond: number | null | undefined): string {
  if (!bytesPerSecond) return "—";
  return `${formatFileSize(bytesPerSecond)}/s`;
}

export function formatEta(seconds: number | null | undefined): string {
  if (!seconds && seconds !== 0) return "—";
  if (seconds < 60) return `${Math.round(seconds)}s left`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m left`;
  return `${Math.floor(minutes / 60)}h ${minutes % 60}m left`;
}
