"use client";

import { Toaster } from "@/components/ui/sonner";

import { ModalProvider } from "./modal-provider";
import { QueryProvider } from "./query-provider";
import { ThemeProvider } from "./theme-provider";

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <QueryProvider>
        <ModalProvider>
          {children}
          <Toaster position="bottom-right" />
        </ModalProvider>
      </QueryProvider>
    </ThemeProvider>
  );
}
