export interface VideoOption {
  id: string;
  kind: "video";
  height: number;
  label: string;
  fps: number | null;
  video_codec: string;
  audio_codec: string;
  container: string;
  needs_merge: boolean;
  size_bytes: number | null;
  size_is_estimate: boolean;
  requires_po_token: boolean;
}

export interface AudioOption {
  id: string;
  kind: "audio";
  label: string;
  container: string;
  codec: string;
  bitrate_kbps: number | null;
  size_bytes: number | null;
  size_is_estimate: boolean;
  is_passthrough: boolean;
}

export interface FormatCatalogue {
  video: VideoOption[];
  audio: AudioOption[];
}
