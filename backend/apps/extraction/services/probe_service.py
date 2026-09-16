"""Read a YouTube URL and return something the UI can render."""

from datetime import timedelta

from django.utils import timezone

from ..domain.canonical_url import CanonicalUrl
from ..domain.error_code import ErrorCode
from ..domain.exceptions import ExtractionError
from ..domain.media_kind import SourceKind
from ..domain.probe_result import VideoProbe
from ..options.probe_options import video_probe_options
from .format_normalizer import FormatNormalizer
from .ytdlp_client import YtDlpClient

# Metadata stays valid for days, but format URLs are signed and IP-bound and
# expire in roughly six hours. We never store those URLs, so this TTL only
# governs how fresh the format list is.
PROBE_TTL = timedelta(hours=6)


class ProbeService:
    def __init__(self, client: YtDlpClient | None = None) -> None:
        self.client = client or YtDlpClient()
        self.normalizer = FormatNormalizer()

    def probe_video(self, canonical: CanonicalUrl) -> VideoProbe:
        options = video_probe_options(logger=self.client.logger)
        info = self.client.extract(canonical.url, options, download=False)

        if info.get("is_live"):
            raise ExtractionError(ErrorCode.LIVE_NOT_SUPPORTED, canonical.external_id)

        formats, subtitles = self.normalizer.build(info)
        if not formats.video and not formats.audio:
            raise ExtractionError(ErrorCode.EXTRACTOR_ERROR, "no usable formats")

        return VideoProbe(
            source_kind=SourceKind.VIDEO,
            video_id=info.get("id") or canonical.external_id,
            title=info.get("title") or "Untitled",
            channel=info.get("channel") or info.get("uploader") or "",
            duration=info.get("duration"),
            thumbnail_url=self._thumbnail(info),
            is_live=bool(info.get("is_live")),
            formats=formats,
            subtitles=subtitles,
        )

    @staticmethod
    def expires_at():
        return timezone.now() + PROBE_TTL

    def _thumbnail(self, info: dict) -> str:
        if info.get("thumbnail"):
            return info["thumbnail"]
        thumbnails = info.get("thumbnails") or []
        return thumbnails[-1]["url"] if thumbnails else ""
