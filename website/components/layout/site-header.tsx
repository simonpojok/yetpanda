"use client";

import { Download } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useModal } from "@/providers/modal-provider";

import { ThemeToggle } from "./theme-toggle";

export function SiteHeader({ activeCount }: { activeCount: number }) {
  const { open } = useModal();

  return (
    <header className="border-border/80 sticky top-0 z-40 border-b bg-background/85 backdrop-blur">
      <div className="mx-auto flex h-14 w-full max-w-5xl items-center justify-between px-4">
        <span className="font-display text-[15px] font-700 tracking-[0.18em] uppercase">
          Yet<span className="text-muted-foreground">Panda</span>
        </span>

        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => open({ name: "queue" })}
            className="gap-2"
          >
            <Download className="size-4" />
            Downloads
            {activeCount > 0 && (
              <span className="tabular ml-0.5 rounded-[4px] bg-signal px-1.5 py-0.5 text-[11px] font-medium text-signal-foreground">
                {activeCount}
              </span>
            )}
          </Button>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
