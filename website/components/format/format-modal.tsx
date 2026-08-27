"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useCreateJob } from "@/hooks/use-create-job";
import { useDownloadSession } from "@/hooks/use-download-session";
import type { VideoProbe } from "@/lib/domain/probe";
import type { SubtitleMode } from "@/lib/domain/subtitle-track";
import { formatDuration } from "@/lib/format/format-duration";
import { useModal } from "@/providers/modal-provider";

import { AudioBitrateOption } from "./audio-bitrate-option";
import { SubtitleSection } from "./subtitle-section";
import { VideoFormatRow } from "./video-format-row";

export function FormatModal({ probe }: { probe: VideoProbe }) {
  const { close, open } = useModal();
  const { addJob } = useDownloadSession();

  const [tab, setTab] = useState<"video" | "audio">("video");
  const [videoId, setVideoId] = useState(probe.formats.video[0]?.id ?? "");
  const [audioId, setAudioId] = useState(probe.formats.audio[0]?.id ?? "");
  const [subtitleMode, setSubtitleMode] = useState<SubtitleMode>("none");
  const [subtitleLangs, setSubtitleLangs] = useState<string[]>([]);

  const createJob = useCreateJob((jobId) => {
    addJob(jobId);
    close();
    open({ name: "queue" });
  });

  const submit = () => {
    if (tab === "video") {
      const option = probe.formats.video.find((o) => o.id === videoId);
      if (!option) return;
      createJob.mutate({
        url: probe.source_url,
        kind: "video",
        height: option.height,
        subtitle_mode: subtitleMode,
        subtitle_langs: subtitleMode === "none" ? [] : subtitleLangs,
      });
      return;
    }

    const option = probe.formats.audio.find((o) => o.id === audioId);
    if (!option) return;
    createJob.mutate({
      url: probe.source_url,
      kind: "audio",
      passthrough: option.is_passthrough,
      audio_bitrate_kbps: option.is_passthrough
        ? undefined
        : (option.bitrate_kbps ?? undefined),
    });
  };

  const subtitlesIncomplete = subtitleMode !== "none" && subtitleLangs.length === 0;

  return (
    <Dialog open onOpenChange={close}>
      <DialogContent className="max-h-[88vh] gap-0 overflow-hidden p-0 sm:max-w-lg">
        <DialogHeader className="p-4 pb-3 text-left">
          <DialogTitle className="line-clamp-2 text-base leading-snug">
            {probe.title}
          </DialogTitle>
          <DialogDescription className="tabular text-xs">
            {probe.channel} · {formatDuration(probe.duration)}
          </DialogDescription>
        </DialogHeader>

        <Separator />

        <Tabs value={tab} onValueChange={(value) => setTab(value as "video" | "audio")}>
          <div className="px-4 pt-3">
            <TabsList className="w-full">
              <TabsTrigger value="video" className="flex-1">
                Video
              </TabsTrigger>
              <TabsTrigger value="audio" className="flex-1">
                Audio
              </TabsTrigger>
            </TabsList>
          </div>

          <ScrollArea className="max-h-[46vh]">
            <TabsContent value="video" className="mt-0 space-y-4 p-4">
              <div className="space-y-1.5">
                {probe.formats.video.map((option) => (
                  <VideoFormatRow
                    key={option.id}
                    option={option}
                    selected={option.id === videoId}
                    onSelect={() => setVideoId(option.id)}
                  />
                ))}
              </div>

              <div className="space-y-2">
                <p className="text-muted-foreground text-[11px] tracking-[0.14em] uppercase">
                  Subtitles
                </p>
                <SubtitleSection
                  tracks={probe.subtitles}
                  mode={subtitleMode}
                  langs={subtitleLangs}
                  onModeChange={setSubtitleMode}
                  onLangsChange={setSubtitleLangs}
                  allowEmbed
                />
              </div>
            </TabsContent>

            <TabsContent value="audio" className="mt-0 space-y-1.5 p-4">
              {probe.formats.audio.map((option) => (
                <AudioBitrateOption
                  key={option.id}
                  option={option}
                  selected={option.id === audioId}
                  onSelect={() => setAudioId(option.id)}
                />
              ))}
            </TabsContent>
          </ScrollArea>
        </Tabs>

        <Separator />

        <DialogFooter className="p-4">
          <Button variant="ghost" onClick={close}>
            Cancel
          </Button>
          <Button
            onClick={submit}
            disabled={createJob.isPending || subtitlesIncomplete}
          >
            {createJob.isPending ? "Starting" : "Download"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
