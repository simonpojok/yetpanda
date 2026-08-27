"""Options shared by every yt-dlp invocation.

``allowed_extractors`` and ``default_search`` are defence in depth behind the
URL canonicaliser: even if a parsing bug let something through, no generic
extractor and no search fallback can run. The coming-soon platforms are
deliberately absent - adding them "so it's ready" is how an allowlist quietly
stops being an allowlist.
"""

from django.conf import settings

ALLOWED_EXTRACTORS = ["youtube", "youtube:tab", "youtube:playlist"]


def base_options(logger=None) -> dict:
    options = {
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "noplaylist": True,
        "default_search": "error",
        "allowed_extractors": ALLOWED_EXTRACTORS,
        "socket_timeout": 20,
        "retries": 3,
        "fragment_retries": 5,
        "extractor_retries": 3,
        "file_access_retries": 3,
        # Re-extract instead of crawling when YouTube throttles us.
        "throttledratelimit": 100 * 1024,
        "concurrent_fragment_downloads": 4,
        "cachedir": str(settings.YTDLP_CACHE_DIR),
        "ignoreerrors": False,
        "overwrites": True,
        "trim_file_name": 150,
        "http_headers": {"Accept-Language": "en-US,en;q=0.9"},
        "ffmpeg_location": settings.FFMPEG_PATH,
    }
    if logger is not None:
        options["logger"] = logger
    if settings.YTDLP_COOKIEFILE:
        options["cookiefile"] = settings.YTDLP_COOKIEFILE
    return options
