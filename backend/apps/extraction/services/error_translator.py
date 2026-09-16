"""Map yt-dlp exceptions onto stable API error codes.

This is unavoidably string-matching: yt-dlp exposes no structured reason
codes. Keep the table in one place with a test per entry, and expect to
maintain it whenever upstream rewords a message.
"""

from yt_dlp.utils import DownloadCancelled, DownloadError, ExtractorError, GeoRestrictedError

from ..domain.error_code import ErrorCode

# Ordered: the first match wins, so put specific phrases above general ones.
_PATTERNS: tuple[tuple[str, ErrorCode], ...] = (
    ("sign in to confirm you're not a bot", ErrorCode.BOT_CHECK),
    ("sign in to confirm your age", ErrorCode.AGE_RESTRICTED),
    ("confirm you're not a bot", ErrorCode.BOT_CHECK),
    ("failed to extract any player response", ErrorCode.BOT_CHECK),
    ("members-only", ErrorCode.MEMBERS_ONLY),
    ("join this channel", ErrorCode.MEMBERS_ONLY),
    ("private video", ErrorCode.PRIVATE),
    ("this video is private", ErrorCode.PRIVATE),
    ("age-restricted", ErrorCode.AGE_RESTRICTED),
    ("inappropriate for some users", ErrorCode.AGE_RESTRICTED),
    ("not available in your country", ErrorCode.GEO_BLOCKED),
    ("blocked it in your country", ErrorCode.GEO_BLOCKED),
    ("video unavailable", ErrorCode.NOT_FOUND),
    ("video has been removed", ErrorCode.NOT_FOUND),
    ("does not exist", ErrorCode.NOT_FOUND),
    ("this live event will begin", ErrorCode.LIVE_NOT_SUPPORTED),
    ("is live", ErrorCode.LIVE_NOT_SUPPORTED),
    ("drm", ErrorCode.DRM_PROTECTED),
    ("file is larger than max-filesize", ErrorCode.TOO_LARGE),
    ("no space left on device", ErrorCode.DISK_FULL),
    ("http error 429", ErrorCode.THROTTLED),
    ("too many requests", ErrorCode.THROTTLED),
    ("http error 403", ErrorCode.EXTRACTOR_ERROR),
    ("unable to download webpage", ErrorCode.NETWORK),
    ("connection reset", ErrorCode.NETWORK),
    ("timed out", ErrorCode.NETWORK),
    ("postprocessing", ErrorCode.POSTPROCESS_FAILED),
)


class ErrorTranslator:
    def translate(self, exc: BaseException) -> ErrorCode:
        if isinstance(exc, DownloadCancelled):
            return ErrorCode.CANCELLED
        if isinstance(exc, GeoRestrictedError):
            return ErrorCode.GEO_BLOCKED

        message = str(getattr(exc, "msg", "") or exc).lower()
        for needle, code in _PATTERNS:
            if needle in message:
                return code

        if isinstance(exc, (ExtractorError, DownloadError)):
            return ErrorCode.EXTRACTOR_ERROR
        if isinstance(exc, OSError):
            return ErrorCode.NETWORK
        return ErrorCode.UNKNOWN
