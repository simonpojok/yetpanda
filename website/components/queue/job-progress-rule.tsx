import { cn } from "@/lib/utils";

/**
 * Progress as a 2px rule running the full width, not a rounded pill.
 * At fifty simultaneous rows hairlines stay readable where pills become noise.
 */
export function JobProgressRule({
  percent,
  tone,
}: {
  percent: number;
  tone: "signal" | "done" | "fault" | "idle";
}) {
  const colour = {
    signal: "bg-signal",
    done: "bg-done",
    fault: "bg-fault",
    idle: "bg-muted-foreground/30",
  }[tone];

  return (
    <div className="bg-border/60 h-[2px] w-full">
      <div
        className={cn("h-full transition-[width] duration-500 ease-out", colour)}
        style={{ width: `${Math.min(100, Math.max(0, percent))}%` }}
      />
    </div>
  );
}
