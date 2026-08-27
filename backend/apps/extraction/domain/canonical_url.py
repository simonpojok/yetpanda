"""The only URL shape we ever hand to yt-dlp."""

from dataclasses import dataclass

from .media_kind import SourceKind


@dataclass(frozen=True, slots=True)
class CanonicalUrl:
    source_kind: SourceKind
    external_id: str
    url: str
