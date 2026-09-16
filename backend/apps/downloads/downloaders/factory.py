"""Pick the downloader for a job spec."""

from apps.extraction.domain.media_kind import MediaKind

from .audio import AudioDownloader
from .base import BaseDownloader
from .video import VideoDownloader


class DownloaderFactory:
    def for_job(self, kind: str, spec: dict, client, hooks: dict) -> BaseDownloader:
        if kind == MediaKind.AUDIO:
            return AudioDownloader(
                client, hooks, passthrough=bool(spec.get("passthrough"))
            )
        return VideoDownloader(client, hooks)
