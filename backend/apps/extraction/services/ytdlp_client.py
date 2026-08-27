"""Thin wrapper over ``yt_dlp.YoutubeDL``.

The library API is used everywhere rather than a subprocess: it returns
structured info dicts, gives real progress hooks, and lets cancellation abort
exactly. Crash isolation - subprocess's only real advantage - is already
provided by Celery's prefork pool recycling children.
"""

import logging

from yt_dlp import YoutubeDL

from ..domain.exceptions import ExtractionError
from .error_translator import ErrorTranslator

logger = logging.getLogger(__name__)


class _YtDlpLogger:
    """Keeps yt-dlp off stdout and out of the API response."""

    def debug(self, msg: str) -> None:
        if msg.startswith("[debug] "):
            return
        logger.debug("yt-dlp: %s", msg)

    def info(self, msg: str) -> None:
        logger.debug("yt-dlp: %s", msg)

    def warning(self, msg: str) -> None:
        logger.warning("yt-dlp: %s", msg)

    def error(self, msg: str) -> None:
        logger.error("yt-dlp: %s", msg)


class YtDlpClient:
    def __init__(self) -> None:
        self.logger = _YtDlpLogger()
        self._translator = ErrorTranslator()

    def extract(self, url: str, options: dict, download: bool = False) -> dict:
        """Run an extraction, converting failures into domain errors."""
        try:
            with YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=download)
                # sanitize_info strips unserialisable objects and internals,
                # which is required before anything reaches JSONB.
                return ydl.sanitize_info(info)
        except Exception as exc:  # noqa: BLE001 - translated immediately
            code = self._translator.translate(exc)
            raise ExtractionError(code, str(exc)) from exc

    def prepare_filename(self, info: dict, options: dict) -> str:
        with YoutubeDL(options) as ydl:
            return ydl.prepare_filename(info)
