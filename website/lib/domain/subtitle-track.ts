export interface SubtitleTrack {
  lang: string;
  label: string;
  is_auto: boolean;
}

export type SubtitleMode = "none" | "separate" | "embed";
