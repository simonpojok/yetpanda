"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useModal } from "@/providers/modal-provider";

export function PrivacyModal() {
  const { close } = useModal();

  return (
    <Dialog open onOpenChange={close}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Privacy</DialogTitle>
        </DialogHeader>
        <ScrollArea className="max-h-[60vh] pr-4">
          <div className="text-muted-foreground space-y-3 text-sm">
            <p>There are no accounts. We never ask for an email address.</p>
            <p>
              A cookie identifies your browser so your downloads stay yours and
              so limits can be applied fairly. Your IP address is never stored -
              only a salted hash of it, used to stop abuse.
            </p>
            <p>
              Downloaded files are deleted from the server within a few hours.
              Records of what was downloaded are deleted within seven days.
            </p>
            <p>
              The list of downloads you see lives in your browser tab and
              disappears when you close it.
            </p>
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
