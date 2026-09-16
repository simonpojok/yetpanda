import type { ReactNode } from "react";

import { ReadoutThumbnail } from "./readout-thumbnail";

/**
 * The one component the product is remembered by: a thumbnail, a title, and a
 * row of monospace stats. The hero becomes one on paste, and every queue row
 * reuses it.
 */
export function ReadoutStrip({
  thumbnail,
  title,
  subtitle,
  stats,
  actions,
  footer,
  compact = false,
}: {
  thumbnail: string;
  title: string;
  subtitle?: string;
  stats?: ReactNode;
  actions?: ReactNode;
  footer?: ReactNode;
  compact?: boolean;
}) {
  return (
    <div className="relative">
      <div className="flex items-start gap-3 p-3 sm:gap-4 sm:p-4">
        <ReadoutThumbnail src={thumbnail} alt="" size={compact ? "sm" : "md"} />

        <div className="min-w-0 flex-1">
          <p className="truncate text-sm leading-snug font-medium" title={title}>
            {title}
          </p>
          {subtitle && (
            <p className="text-muted-foreground mt-0.5 truncate text-xs">{subtitle}</p>
          )}
          {stats && (
            <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1">{stats}</div>
          )}
        </div>

        {actions && <div className="flex shrink-0 items-center gap-1">{actions}</div>}
      </div>
      {footer}
    </div>
  );
}
