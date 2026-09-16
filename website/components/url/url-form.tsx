"use client";

import { ArrowRight, ClipboardPaste, Loader2 } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function UrlForm({
  onSubmit,
  isLoading,
}: {
  onSubmit: (url: string) => void;
  isLoading: boolean;
}) {
  const [value, setValue] = useState("");

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    const trimmed = value.trim();
    if (trimmed) onSubmit(trimmed);
  };

  const pasteFromClipboard = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        setValue(text.trim());
        onSubmit(text.trim());
      }
    } catch {
      // Clipboard permission was refused; typing still works.
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex w-full flex-col gap-2 sm:flex-row">
      <div className="relative flex-1">
        <Input
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder="Paste a YouTube video or playlist link"
          aria-label="YouTube link"
          spellCheck={false}
          autoComplete="off"
          className="h-12 pr-11 text-base"
        />
        <Button
          type="button"
          variant="ghost"
          size="icon"
          onClick={pasteFromClipboard}
          aria-label="Paste from clipboard"
          className="text-muted-foreground absolute top-1.5 right-1.5 size-9"
        >
          <ClipboardPaste className="size-4" />
        </Button>
      </div>

      <Button type="submit" size="lg" disabled={isLoading || !value.trim()} className="h-12 gap-2">
        {isLoading ? (
          <>
            <Loader2 className="size-4 animate-spin" />
            Reading
          </>
        ) : (
          <>
            Continue
            <ArrowRight className="size-4" />
          </>
        )}
      </Button>
    </form>
  );
}
