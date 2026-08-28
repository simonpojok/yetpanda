"use client";

import { useCallback, useMemo, useState } from "react";

export interface Pagination<T> {
  items: T[];
  page: number;
  totalPages: number;
  total: number;
  /** 1-based index of the first item on this page, for "3–7 of 21". */
  from: number;
  to: number;
  hasPrevious: boolean;
  hasNext: boolean;
  previous: () => void;
  next: () => void;
}

/**
 * Slices a list into pages.
 *
 * The current page is *derived* during render rather than corrected in an
 * effect: downloads expire on a TTL, so the list shrinks underneath the user,
 * and clamping in an effect would render one frame of an empty page first.
 */
export function usePagination<T>(items: T[], pageSize: number): Pagination<T> {
  const [requestedPage, setRequestedPage] = useState(1);

  const total = items.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const page = Math.min(Math.max(requestedPage, 1), totalPages);

  const pageItems = useMemo(
    () => items.slice((page - 1) * pageSize, page * pageSize),
    [items, page, pageSize],
  );

  const previous = useCallback(() => setRequestedPage((p) => Math.max(1, p - 1)), []);
  const next = useCallback(() => setRequestedPage((p) => p + 1), []);

  return {
    items: pageItems,
    page,
    totalPages,
    total,
    from: total === 0 ? 0 : (page - 1) * pageSize + 1,
    to: Math.min(page * pageSize, total),
    hasPrevious: page > 1,
    hasNext: page < totalPages,
    previous,
    next,
  };
}