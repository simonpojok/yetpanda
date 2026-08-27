"use client";

import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { useCreateBatch } from "@/hooks/use-create-batch";
import { useDownloadSession } from "@/hooks/use-download-session";
import type { PlaylistProbe } from "@/lib/domain/probe";
import { formatDuration } from "@/lib/format/format-duration";
import { useModal } from "@/providers/modal-provider";

import { PlaylistItemRow } from "./playlist-item-row";

const HEIGHTS = [2160, 1440, 1080, 720, 480, 360];
const BITRATES = [320, 256, 192, 128];

export function PlaylistModal({ probe }: { probe: PlaylistProbe }) {
  const { close, open } = useModal();
  const { addBatch } = useDownloadSession();

  const available = useMemo(
    () => probe.entries.filter((entry) => entry.is_available),
    [probe.entries],
  );

  const [kind, setKind] = useState<"video" | "audio">("audio");
  const [height, setHeight] = useState(720);
  const [bitrate, setBitrate] = useState(192);
  const [filter, setFilter] = useState("");
  const [selected, setSelected] = useState<Set<number>>(
    () => new Set(available.map((entry) => entry.index)),
  );

  const createBatch = useCreateBatch((batchId) => {
    addBatch(batchId);
    close();
    open({ name: "queue" });
  });

  const visible = useMemo(() => {
    const needle = filter.trim().toLowerCase();
    return needle
      ? available.filter((entry) => entry.title.toLowerCase().includes(needle))
      : available;
  }, [available, filter]);

  const allSelected = selected.size === available.length && available.length > 0;

  const toggle = (index: number) => {
    setSelected((previous) => {
      const next = new Set(previous);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  };

  const submit = () => {
    createBatch.mutate({
      url: probe.source_url,
      kind,
      height: kind === "video" ? height : undefined,
      audio_bitrate_kbps: kind === "audio" ? bitrate : undefined,
      item_indexes: allSelected ? undefined : [...selected],
    });
  };

  return (
    <Dialog open onOpenChange={close}>
      <DialogContent className="max-h-[88vh] gap-0 overflow-hidden p-0 sm:max-w-2xl">
        <DialogHeader className="p-4 pb-3 text-left">
          <DialogTitle className="line-clamp-1 text-base">{probe.title}</DialogTitle>
          <DialogDescription className="tabular text-xs">
            {probe.channel} · {probe.item_count} items ·{" "}
            {formatDuration(probe.total_duration)}
          </DialogDescription>
        </DialogHeader>

        <Separator />

        <div className="flex flex-col gap-2 p-4 sm:flex-row">
          <Select value={kind} onValueChange={(value) => setKind(value as "video" | "audio")}>
            <SelectTrigger className="sm:w-32">
              <SelectValue placeholder="Choose a format" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="audio">MP3</SelectItem>
              <SelectItem value="video">MP4</SelectItem>
            </SelectContent>
          </Select>

          {kind === "video" ? (
            <Select value={String(height)} onValueChange={(v) => setHeight(Number(v))}>
              <SelectTrigger className="sm:w-40">
                <SelectValue placeholder="Choose a quality" />
              </SelectTrigger>
              <SelectContent>
                {HEIGHTS.map((value) => (
                  <SelectItem key={value} value={String(value)}>
                    {value}p
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          ) : (
            <Select value={String(bitrate)} onValueChange={(v) => setBitrate(Number(v))}>
              <SelectTrigger className="sm:w-40">
                <SelectValue placeholder="Choose a bitrate" />
              </SelectTrigger>
              <SelectContent>
                {BITRATES.map((value) => (
                  <SelectItem key={value} value={String(value)}>
                    {value} kbps
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}

          <Input
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
            placeholder="Filter items by title"
            aria-label="Filter items by title"
            className="flex-1"
          />
        </div>

        <div className="border-border/80 flex items-center gap-2 border-y px-4 py-2">
          <Checkbox
            checked={allSelected}
            onCheckedChange={() =>
              setSelected(allSelected ? new Set() : new Set(available.map((e) => e.index)))
            }
            aria-label="Select every item"
          />
          <span className="text-muted-foreground text-xs">
            {selected.size} of {available.length} selected
            {probe.entries.length > available.length &&
              ` · ${probe.entries.length - available.length} unavailable`}
          </span>
        </div>

        <ScrollArea className="h-[38vh]">
          {visible.map((entry) => (
            <PlaylistItemRow
              key={entry.index}
              entry={entry}
              selected={selected.has(entry.index)}
              onToggle={() => toggle(entry.index)}
            />
          ))}
        </ScrollArea>

        <Separator />

        <DialogFooter className="p-4">
          <Button variant="ghost" onClick={close}>
            Cancel
          </Button>
          <Button onClick={submit} disabled={selected.size === 0 || createBatch.isPending}>
            {createBatch.isPending
              ? "Starting"
              : `Download ${selected.size} ${selected.size === 1 ? "item" : "items"}`}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
