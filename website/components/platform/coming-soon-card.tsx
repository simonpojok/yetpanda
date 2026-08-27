import type { Platform } from "@/lib/domain/platform";

export function ComingSoonCard({ platform }: { platform: Platform }) {
  return (
    <div
      aria-disabled
      className="border-border/80 flex items-center justify-between rounded-[4px] border border-dashed px-3 py-2.5 opacity-70"
    >
      <span className="text-sm">{platform.name}</span>
      <span className="text-muted-foreground text-[10px] tracking-[0.14em] uppercase">
        Soon
      </span>
    </div>
  );
}
