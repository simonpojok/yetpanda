"""What the user asked for: a video file or an audio file."""

from enum import StrEnum


class MediaKind(StrEnum):
    VIDEO = "video"
    AUDIO = "audio"


class SubtitleMode(StrEnum):
    NONE = "none"
    SEPARATE = "separate"
    EMBED = "embed"


class SourceKind(StrEnum):
    VIDEO = "video"
    PLAYLIST = "playlist"
