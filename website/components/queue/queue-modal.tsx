"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useBatchList } from "@/hooks/use-batch-list";
import { useDownloadSession } from "@/hooks/use-download-session";
import { useJobPolling } from "@/hooks/use-job-polling";
import { isTerminal } from "@/lib/domain/job";
import { useModal } from "@/providers/modal-provider";

import { QueueList } from "./queue-list";

export function QueueModal() {
  const { close } = useModal();
  const { jobIds, batchIds } = useDownloadSession();
  const { data: jobs = [] } = useJobPolling(jobIds);
  const batches = useBatchList(batchIds);

  const active = jobs.filter((job) => !isTerminal(job.status));
  const finished = jobs.filter((job) => isTerminal(job.status));
  const activeCount = active.length + batches.active.length;
  const finishedCount = finished.length + batches.finished.length;

  return (
    <Dialog open onOpenChange={close}>
      <DialogContent className="max-h-[min(44rem,calc(100dvh-4rem))] w-[calc(100%-2rem)] gap-0 overflow-hidden p-0 sm:max-w-xl">
        <DialogHeader className="p-4 pb-3 text-left">
          <DialogTitle className="text-base">Downloads</DialogTitle>
          <DialogDescription className="text-xs">
            Files stay on the server for a couple of hours. Save what you want to keep.
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="active" className="min-h-0 flex-auto">
          <div className="shrink-0 px-4">
            <TabsList className="w-full">
              <TabsTrigger value="active" className="flex-1">
                Active {activeCount > 0 && `(${activeCount})`}
              </TabsTrigger>
              <TabsTrigger value="finished" className="flex-1">
                Finished {finishedCount > 0 && `(${finishedCount})`}
              </TabsTrigger>
            </TabsList>
          </div>

          {/* A plain overflow container, not Radix's ScrollArea. ScrollArea's
            viewport is `height: 100%`, which will not resolve against a parent
            sized by flex *shrinking* - it sized to content and overflowed.
            Insetting it fixed scrolling but put the content out of flow, so the
            dialog no longer knew how tall it wanted to be and collapsed to its
            floor. A flex item with `min-h-0` + `overflow-y-auto` satisfies both:
            its content is the flex basis, so the dialog grows to fit, and it
            scrolls once max-height clamps it. */}
          <div className="min-h-40 flex-auto overflow-y-auto">
            <TabsContent value="active" className="mt-3 pb-4">
              <QueueList
                batches={batches.active}
                jobs={active}
                show="active"
                emptyMessage="Nothing downloading. Paste a link to start."
              />
            </TabsContent>

            <TabsContent value="finished" className="mt-3 pb-4">
              <QueueList
                batches={batches.finished}
                jobs={finished}
                show="finished"
                emptyMessage="Finished downloads will appear here."
              />
            </TabsContent>
          </div>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
