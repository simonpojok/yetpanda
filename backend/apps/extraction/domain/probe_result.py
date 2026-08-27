"""Normalised output of a probe, independent of yt-dlp's shape."""

from dataclasses import dataclass, field

from .media_format import FormatCatalogue
from .media_kind import SourceKind
from .subtitle_track import SubtitleTrack


@dataclass(frozen=True, slots=True)
class VideoProbe:
    source_kind: SourceKind
    video_id: str
    title: str
    channel: str
    duration: int | None
    thumbnail_url: str
    is_live: bool
    formats: FormatCatalogue
    subtitles: list[SubtitleTrack] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "kind": "video",
            "video_id": self.video_id,
            "title": self.title,
            "channel": self.channel,
            "duration": self.duration,
            "thumbnail_url": self.thumbnail_url,
            "is_live": self.is_live,
            "formats": self.formats.as_dict(),
            "subtitles": [s.as_dict() for s in self.subtitles],
        }


@dataclass(frozen=True, slots=True)
class PlaylistEntry:
    index: int
    video_id: str
    title: str
    duration: int | None
    thumbnail_url: str
    is_available: bool

    def as_dict(self) -> dict:
        return {
            "index": self.index,
            "video_id": self.video_id,
            "title": self.title,
            "duration": self.duration,
            "thumbnail_url": self.thumbnail_url,
            "is_available": self.is_available,
        }


@dataclass(frozen=True, slots=True)
class PlaylistProbe:
    source_kind: SourceKind
    playlist_id: str
    title: str
    channel: str
    entries: list[PlaylistEntry]

    @property
    def total_duration(self) -> int:
        return sum(e.duration or 0 for e in self.entries if e.is_available)

    def as_dict(self) -> dict:
        return {
            "kind": "playlist",
            "playlist_id": self.playlist_id,
            "title": self.title,
            "channel": self.channel,
            "item_count": len(self.entries),
            "total_duration": self.total_duration,
            "entries": [e.as_dict() for e in self.entries],
        }
