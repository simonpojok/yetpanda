"use client";

import { useModal } from "@/providers/modal-provider";

export function SiteFooter() {
  const { open } = useModal();

  return (
    <footer className="border-border/80 mt-auto border-t">
      <div className="text-muted-foreground mx-auto flex w-full max-w-5xl flex-col gap-2 px-4 py-6 text-xs sm:flex-row sm:items-center sm:justify-between">
        <p>You are responsible for having the rights to what you download.</p>
        <div className="flex gap-4">
          <button
            type="button"
            className="hover:text-foreground underline-offset-4 hover:underline"
            onClick={() => open({ name: "terms" })}
          >
            Terms
          </button>
          <button
            type="button"
            className="hover:text-foreground underline-offset-4 hover:underline"
            onClick={() => open({ name: "privacy" })}
          >
            Privacy
          </button>
        </div>
      </div>
    </footer>
  );
}
