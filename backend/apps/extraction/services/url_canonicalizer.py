"""Turn arbitrary user input into a URL we constructed ourselves.

This is the SSRF boundary. yt-dlp's generic extractor will happily fetch
``http://169.254.169.254/`` or our own Redis, so the raw string a user typed
must never reach it. We parse out the id and rebuild the URL from a literal
template; anything we cannot parse is rejected outright.
"""

import re
from urllib.parse import parse_qs, urlsplit

from ..domain.canonical_url import CanonicalUrl
from ..domain.error_code import ErrorCode
from ..domain.exceptions import UnsupportedUrlError
from ..domain.media_kind import SourceKind

MAX_URL_LENGTH = 2048

ALLOWED_HOSTS = frozenset(
    {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
        "youtu.be",
        "www.youtu.be",
        "youtube-nocookie.com",
        "www.youtube-nocookie.com",
    }
)

_VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
_PLAYLIST_ID = re.compile(r"^[A-Za-z0-9_-]{12,42}$")

# Auto-generated mixes and radio have no fixed length and cannot be expanded.
_UNEXPANDABLE_PLAYLIST_PREFIXES = ("RD", "UL", "LL", "MM")

_ID_PATH_PREFIXES = ("/shorts/", "/embed/", "/live/", "/v/")


class UrlCanonicalizer:
    """Parses a user-supplied string into a :class:`CanonicalUrl`."""

    def canonicalize(self, raw: str) -> CanonicalUrl:
        url = (raw or "").strip()
        if not url or len(url) > MAX_URL_LENGTH:
            raise UnsupportedUrlError(ErrorCode.INVALID_URL, "empty or oversized url")

        if "://" not in url:
            url = f"https://{url}"

        parts = urlsplit(url)
        if parts.scheme not in ("http", "https") or not parts.hostname:
            raise UnsupportedUrlError(ErrorCode.INVALID_URL, "unparseable url")

        host = parts.hostname.lower().rstrip(".")
        if host not in ALLOWED_HOSTS:
            raise UnsupportedUrlError(ErrorCode.UNSUPPORTED_HOST, host)

        query = parse_qs(parts.query)
        playlist_id = self._playlist_id(query)
        if playlist_id:
            return CanonicalUrl(
                source_kind=SourceKind.PLAYLIST,
                external_id=playlist_id,
                url=f"https://www.youtube.com/playlist?list={playlist_id}",
            )

        video_id = self._video_id(host, parts.path, query)
        if video_id:
            return CanonicalUrl(
                source_kind=SourceKind.VIDEO,
                external_id=video_id,
                url=f"https://www.youtube.com/watch?v={video_id}",
            )

        raise UnsupportedUrlError(ErrorCode.INVALID_URL, "no video or playlist id found")

    def _playlist_id(self, query: dict[str, list[str]]) -> str | None:
        candidate = (query.get("list") or [""])[0]
        if not candidate or not _PLAYLIST_ID.match(candidate):
            return None
        if candidate.startswith(_UNEXPANDABLE_PLAYLIST_PREFIXES):
            return None
        return candidate

    def _video_id(self, host: str, path: str, query: dict[str, list[str]]) -> str | None:
        if host.endswith("youtu.be"):
            candidate = path.lstrip("/").split("/")[0]
        elif path.rstrip("/") == "/watch":
            candidate = (query.get("v") or [""])[0]
        elif path.startswith(_ID_PATH_PREFIXES):
            segments = path.split("/")
            candidate = segments[2] if len(segments) > 2 else ""
        else:
            candidate = ""
        return candidate if _VIDEO_ID.match(candidate) else None
