"use client";

import { Download } from "lucide-react";
import { useRef } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { fileUrl } from "@/lib/api/http-client";
import type { Job } from "@/lib/domain/job";
import { formatFileSize } from "@/lib/format/format-file-size";
import { useModal } from "@/providers/modal-provider";

export function PlayerModal({ job }: { job: Job }) {
  const { close } = useModal();
  const mediaRef = useRef<HTMLVideoElement & HTMLAudioElement>(null);

  if (!job.result) return null;

  const src = fileUrl(job.result.stream_url);
  const isAudio = job.kind === "audio";

  return (
    <Dialog open onOpenChange={close}>
      <DialogContent className="max-h-[calc(100dvh-4rem)] gap-0 overflow-hidden p-0 sm:max-w-2xl">
        <DialogHeader className="p-4 pb-3 text-left">
          <DialogTitle className="line-clamp-1 text-base">{job.title}</DialogTitle>
          <DialogDescription className="tabular text-xs">
            {job.channel} · {formatFileSize(job.result.size_bytes)}
          </DialogDescription>
        </DialogHeader>

        <div className="shrink-0 bg-black">
          {isAudio ? (
            <div className="p-6">
              {/* No crossOrigin attribute: a plain media load needs no CORS,
                  it just sends Range and gets 206 back. */}
              <audio ref={mediaRef} src={src} controls autoPlay className="w-full" />
            </div>
          ) : (
            <video
              ref={mediaRef}
              src={src}
              controls
              autoPlay
              playsInline
              className="max-h-[60vh] w-full"
            />
          )}
        </div>

        <DialogFooter>
          <Button variant="ghost" onClick={close}>
            Close
          </Button>
          <Button asChild className="gap-2">
            <a href={fileUrl(job.result.download_url)} download>
              <Download className="size-4" />
              Save file
            </a>
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
