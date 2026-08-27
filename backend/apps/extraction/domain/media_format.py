"""A single downloadable option shown in the UI."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class VideoOption:
    """One selectable video quality, keyed by height rather than format id."""

    id: str
    height: int
    label: str
    fps: int | None
    video_codec: str
    audio_codec: str
    container: str
    needs_merge: bool
    size_bytes: int | None
    size_is_estimate: bool
    requires_po_token: bool = False

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "kind": "video",
            "height": self.height,
            "label": self.label,
            "fps": self.fps,
            "video_codec": self.video_codec,
            "audio_codec": self.audio_codec,
            "container": self.container,
            "needs_merge": self.needs_merge,
            "size_bytes": self.size_bytes,
            "size_is_estimate": self.size_is_estimate,
            "requires_po_token": self.requires_po_token,
        }


@dataclass(frozen=True, slots=True)
class AudioOption:
    """One selectable audio output. Bitrate is the *target*, not the source."""

    id: str
    label: str
    container: str
    codec: str
    bitrate_kbps: int | None
    size_bytes: int | None
    size_is_estimate: bool
    is_passthrough: bool = False

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "kind": "audio",
            "label": self.label,
            "container": self.container,
            "codec": self.codec,
            "bitrate_kbps": self.bitrate_kbps,
            "size_bytes": self.size_bytes,
            "size_is_estimate": self.size_is_estimate,
            "is_passthrough": self.is_passthrough,
        }


@dataclass(frozen=True, slots=True)
class FormatCatalogue:
    """Everything the format picker needs for one video."""

    video: list[VideoOption] = field(default_factory=list)
    audio: list[AudioOption] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "video": [o.as_dict() for o in self.video],
            "audio": [o.as_dict() for o in self.audio],
        }
