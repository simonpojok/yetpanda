"use client";

import { FormatModal } from "@/components/format/format-modal";
import { PrivacyModal } from "@/components/legal/privacy-modal";
import { TermsModal } from "@/components/legal/terms-modal";
import { PlayerModal } from "@/components/player/player-modal";
import { PlaylistModal } from "@/components/playlist/playlist-modal";
import { QueueModal } from "@/components/queue/queue-modal";
import { useModal } from "@/providers/modal-provider";

/** Renders whichever modal is on top of the stack. */
export function ModalHost() {
  const { current } = useModal();
  if (!current) return null;

  switch (current.name) {
    case "format":
      return <FormatModal probe={current.probe} />;
    case "playlist":
      return <PlaylistModal probe={current.probe} />;
    case "queue":
      return <QueueModal />;
    case "player":
      return <PlayerModal job={current.job} />;
    case "terms":
      return <TermsModal />;
    case "privacy":
      return <PrivacyModal />;
    default:
      return null;
  }
}
