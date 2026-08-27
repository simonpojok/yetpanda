"use client";

import { createContext, useCallback, useContext, useMemo, useState } from "react";

import type { Batch } from "@/lib/domain/batch";
import type { Job } from "@/lib/domain/job";
import type { PlaylistProbe, VideoProbe } from "@/lib/domain/probe";

type Modal =
  | { name: "format"; probe: VideoProbe }
  | { name: "playlist"; probe: PlaylistProbe }
  | { name: "queue" }
  | { name: "player"; job: Job }
  | { name: "batch"; batch: Batch }
  | { name: "terms" }
  | { name: "privacy" };

interface ModalContextValue {
  current: Modal | null;
  open: (modal: Modal) => void;
  close: () => void;
}

const ModalContext = createContext<ModalContextValue | null>(null);

/**
 * A small stack rather than a single value, so Queue -> Player layers and
 * dismisses back to the queue instead of closing everything.
 */
export function ModalProvider({ children }: { children: React.ReactNode }) {
  const [stack, setStack] = useState<Modal[]>([]);

  const open = useCallback((modal: Modal) => {
    setStack((previous) => [...previous, modal]);
  }, []);

  const close = useCallback(() => {
    setStack((previous) => previous.slice(0, -1));
  }, []);

  const value = useMemo(
    () => ({ current: stack.at(-1) ?? null, open, close }),
    [stack, open, close],
  );

  return <ModalContext.Provider value={value}>{children}</ModalContext.Provider>;
}

export function useModal(): ModalContextValue {
  const context = useContext(ModalContext);
  if (!context) throw new Error("useModal must be used inside ModalProvider");
  return context;
}
