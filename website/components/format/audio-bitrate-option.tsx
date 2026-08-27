import { Check } from "lucide-react";

import { formatFileSize } from "@/lib/format/format-file-size";
import type { AudioOption } from "@/lib/domain/media-format";
import { cn } from "@/lib/utils";

export function AudioBitrateOption({
  option,
  selected,
  onSelect,
}: {
  option: AudioOption;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      aria-pressed={selected}
      className={cn(
        "flex w-full items-center gap-3 rounded-[4px] border px-3 py-2.5 text-left transition-colors",
        selected ? "border-foreground bg-muted" : "border-border hover:bg-muted/60",
      )}
    >
      <span className="flex-1 text-sm font-medium">{option.label}</span>
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
