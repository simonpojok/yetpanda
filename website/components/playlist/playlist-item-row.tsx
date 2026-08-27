import { Checkbox } from "@/components/ui/checkbox";
import type { PlaylistEntry } from "@/lib/domain/probe";
import { formatDuration } from "@/lib/format/format-duration";

export function PlaylistItemRow({
  entry,
  selected,
  onToggle,
}: {
  entry: PlaylistEntry;
  selected: boolean;
  onToggle: () => void;
}) {
  return (
    <label className="border-border/60 hover:bg-muted/50 flex cursor-pointer items-center gap-3 border-b px-4 py-2 last:border-b-0">
      <Checkbox checked={selected} onCheckedChange={onToggle} />
      <span className="tabular text-muted-foreground w-7 shrink-0 text-right text-xs">
        {entry.index + 1}
      </span>
      <span className="min-w-0 flex-1 truncate text-sm" title={entry.title}>
        {entry.title}
      </span>
      <span className="tabular text-muted-foreground shrink-0 text-xs">
        {formatDuration(entry.duration)}
      </span>
    </label>
  );
}
