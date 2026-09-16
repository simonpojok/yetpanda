import type { FormatCatalogue } from "./media-format";
import type { SubtitleTrack } from "./subtitle-track";

export interface VideoProbe {
  kind: "video";
  source_url: string;
  video_id: string;
  title: string;
  channel: string;
  duration: number | null;
  thumbnail_url: string;
  is_live: boolean;
  formats: FormatCatalogue;
  subtitles: SubtitleTrack[];
}

export interface PlaylistEntry {
  index: number;
  video_id: string;
  title: string;
  duration: number | null;
  thumbnail_url: string;
  is_available: boolean;
}

export interface PlaylistProbe {
  kind: "playlist";
  source_url: string;
  playlist_id: string;
  title: string;
  channel: string;
  item_count: number;
  total_duration: number;
  entries: PlaylistEntry[];
}

export type ProbeResult = VideoProbe | PlaylistProbe;
