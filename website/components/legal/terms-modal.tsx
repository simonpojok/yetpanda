"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useModal } from "@/providers/modal-provider";

export function TermsModal() {
  const { close } = useModal();

  return (
    <Dialog open onOpenChange={close}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Terms</DialogTitle>
        </DialogHeader>
        <ScrollArea className="max-h-[60vh] pr-4">
          <div className="text-muted-foreground space-y-3 text-sm">
            <p>
              YetPanda downloads media on your behalf. You are responsible for
              having the right to download and keep whatever you request, and
              for complying with the terms of the site it comes from.
            </p>
            <p>
              Do not use this service for material you do not own or have
              permission to copy.
            </p>
            <p>
              Downloads are capped in length, size and number, and finished
              files are deleted from the server within a few hours. The service
              is provided as-is, with no guarantee that any particular download
              will succeed.
            </p>
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
