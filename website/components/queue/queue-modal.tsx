"use client";

import { Inbox } from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useDownloadSession } from "@/hooks/use-download-session";
import { useJobPolling } from "@/hooks/use-job-polling";
import { isTerminal } from "@/lib/domain/job";
import { useModal } from "@/providers/modal-provider";

import { BatchRow } from "./batch-row";
import { JobRow } from "./job-row";

export function QueueModal() {
  const { close } = useModal();
  const { jobIds, batchIds } = useDownloadSession();
  const { data: jobs = [] } = useJobPolling(jobIds);

  const active = jobs.filter((job) => !isTerminal(job.status));
  const finished = jobs.filter((job) => isTerminal(job.status));

  return (
    <Dialog open onOpenChange={close}>
      <DialogContent className="max-h-[86vh] gap-0 overflow-hidden p-0 sm:max-w-xl">
        <DialogHeader className="p-4 pb-3 text-left">
          <DialogTitle className="text-base">Downloads</DialogTitle>
          <DialogDescription className="text-xs">
            Files stay on the server for a couple of hours. Save what you want to keep.
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="active">
          <div className="px-4">
            <TabsList className="w-full">
              <TabsTrigger value="active" className="flex-1">
                Active {active.length > 0 && `(${active.length})`}
              </TabsTrigger>
              <TabsTrigger value="finished" className="flex-1">
                Finished {finished.length > 0 && `(${finished.length})`}
              </TabsTrigger>
            </TabsList>
          </div>

          <ScrollArea className="h-[54vh]">
            <TabsContent value="active" className="mt-3">
              {batchIds.map((id) => (
                <BatchRow key={id} batchId={id} />
              ))}
              {active.map((job) => (
                <JobRow key={job.id} job={job} />
              ))}
              {active.length === 0 && batchIds.length === 0 && (
                <EmptyState message="Nothing downloading. Paste a link to start." />
              )}
            </TabsContent>

            <TabsContent value="finished" className="mt-3">
              {finished.map((job) => (
                <JobRow key={job.id} job={job} />
              ))}
              {finished.length === 0 && (
                <EmptyState message="Finished downloads will appear here." />
              )}
            </TabsContent>
          </ScrollArea>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="text-muted-foreground flex flex-col items-center gap-2 px-4 py-14 text-center">
      <Inbox className="size-5" />
      <p className="text-sm">{message}</p>
    </div>
  );
}
