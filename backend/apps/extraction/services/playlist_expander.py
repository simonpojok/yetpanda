"""Expand a playlist cheaply enough to render a picker immediately."""

from django.conf import settings

from ..domain.canonical_url import CanonicalUrl
from ..domain.error_code import ErrorCode
from ..domain.exceptions import ExtractionError
from ..domain.media_kind import SourceKind
from ..domain.probe_result import PlaylistEntry, PlaylistProbe
from ..options.probe_options import playlist_probe_options
from .ytdlp_client import YtDlpClient

# yt-dlp surfaces removed entries under these titles rather than omitting them.
_UNAVAILABLE_TITLES = {"[private video]", "[deleted video]", "[unavailable video]"}


class PlaylistExpander:
    def __init__(self, client: YtDlpClient | None = None) -> None:
        self.client = client or YtDlpClient()

    def expand(self, canonical: CanonicalUrl) -> PlaylistProbe:
        """Flat extraction only.

        For a bulk batch the user picks one preference for the whole list, so
        per-item formats are never needed - the same selector string is
        resolved per child at download time.
        """
        options = playlist_probe_options(
            max_items=settings.MAX_BATCH_ITEMS, logger=self.client.logger
        )
        info = self.client.extract(canonical.url, options, download=False)

        entries = self._entries(info)
        if not entries:
            raise ExtractionError(ErrorCode.NOT_FOUND, "playlist has no usable entries")

        return PlaylistProbe(
            source_kind=SourceKind.PLAYLIST,
            playlist_id=info.get("id") or canonical.external_id,
            title=info.get("title") or "Untitled playlist",
            channel=info.get("channel") or info.get("uploader") or "",
            entries=entries,
        )

    def _entries(self, info: dict) -> list[PlaylistEntry]:
        entries = []
        for index, raw in enumerate(info.get("entries") or []):
            if not raw:
                continue
            title = raw.get("title") or "Untitled"
            entries.append(
                PlaylistEntry(
                    index=index,
                    video_id=raw.get("id") or "",
                    title=title,
                    duration=raw.get("duration"),
                    thumbnail_url=self._thumbnail(raw),
                    is_available=title.lower() not in _UNAVAILABLE_TITLES
                    and bool(raw.get("id")),
                )
            )
        return entries

    def _thumbnail(self, entry: dict) -> str:
        thumbnails = entry.get("thumbnails") or []
        return thumbnails[-1]["url"] if thumbnails else ""
