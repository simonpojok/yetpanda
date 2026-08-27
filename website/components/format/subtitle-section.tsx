"use client";

import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { SubtitleMode, SubtitleTrack } from "@/lib/domain/subtitle-track";

export function SubtitleSection({
  tracks,
  mode,
  langs,
  onModeChange,
  onLangsChange,
  allowEmbed,
}: {
  tracks: SubtitleTrack[];
  mode: SubtitleMode;
  langs: string[];
  onModeChange: (mode: SubtitleMode) => void;
  onLangsChange: (langs: string[]) => void;
  allowEmbed: boolean;
}) {
  if (tracks.length === 0) {
    return (
      <p className="text-muted-foreground text-xs">
        This video has no captions.
      </p>
    );
  }

  const toggle = (lang: string) => {
    onLangsChange(
      langs.includes(lang) ? langs.filter((l) => l !== lang) : [...langs, lang],
    );
  };

  return (
    <div className="space-y-3">
      <Select value={mode} onValueChange={(value) => onModeChange(value as SubtitleMode)}>
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Choose how to include subtitles" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="none">No subtitles</SelectItem>
          <SelectItem value="separate">Separate .srt file</SelectItem>
          {allowEmbed && <SelectItem value="embed">Embedded in the video</SelectItem>}
        </SelectContent>
      </Select>

      {mode !== "none" && (
        <ScrollArea className="border-border h-40 rounded-[4px] border">
          <div className="space-y-1 p-2">
            {tracks.map((track) => (
              <label
                key={`${track.lang}-${track.is_auto}`}
                className="hover:bg-muted/60 flex cursor-pointer items-center gap-2 rounded-[4px] px-2 py-1.5"
              >
                <Checkbox
                  checked={langs.includes(track.lang)}
                  onCheckedChange={() => toggle(track.lang)}
                />
                <span className="flex-1 text-sm">{track.label}</span>
                {track.is_auto && (
                  <span className="text-muted-foreground text-[10px] tracking-wide uppercase">
                    auto
                  </span>
                )}
              </label>
            ))}
          </div>
        </ScrollArea>
      )}
    </div>
  );
}
