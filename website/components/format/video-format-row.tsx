import { Check } from "lucide-react";

import { formatFileSize } from "@/lib/format/format-file-size";
import type { VideoOption } from "@/lib/domain/media-format";
import { cn } from "@/lib/utils";

export function VideoFormatRow({
  option,
  selected,
  onSelect,
}: {
  option: VideoOption;
  selected: boolean;
  onSelect: () => void;
}) {
  const disabled = option.requires_po_token;

  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onSelect}
      aria-pressed={selected}
      className={cn(
        "flex w-full items-center gap-3 rounded-[4px] border px-3 py-2.5 text-left transition-colors",
        selected ? "border-foreground bg-muted" : "border-border hover:bg-muted/60",
        disabled && "cursor-not-allowed opacity-45 hover:bg-transparent",
      )}
    >
      <span className="tabular w-16 text-sm font-medium">{option.label}</span>
      <span className="text-muted-foreground flex-1 text-xs">
        {option.video_codec}
        {option.video_codec === "H.264" && (
          <span className="text-done ml-2">most compatible</span>
        )}
        {disabled && <span className="ml-2">unavailable</span>}
      </span>
      <span className="tabular text-muted-foreground text-xs">
        {option.size_is_estimate && option.size_bytes ? "~" : ""}
        {formatFileSize(option.size_bytes)}
      </span>
      <Check
        className={cn("size-4 shrink-0", selected ? "opacity-100" : "opacity-0")}
      />
    </button>
  );
}
