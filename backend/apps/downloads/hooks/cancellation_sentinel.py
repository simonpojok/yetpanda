"""Layer one of cancellation: cooperative, from inside yt-dlp.

Raising ``DownloadCancelled`` from a progress hook is a documented yt-dlp
abort path, and the hook fires several times a second during a download. That
covers the overwhelming majority of cancellations. The SIGTERM handler in the
task covers the rest, because postprocessor hooks only fire at start and
finish - so a six-minute transcode is a blind spot for this layer alone.
"""

import time

from yt_dlp.utils import DownloadCancelled

POLL_INTERVAL_SECONDS = 1.0


class CancellationSentinel:
    """Checks a Redis flag at most once a second, then aborts hard."""

    def __init__(self, job_id: str, redis_client) -> None:
        self._key = f"job:{job_id}:cancel"
        self._redis = redis_client
        self._next_check = 0.0

    def check(self) -> None:
        now = time.monotonic()
        if now < self._next_check:
            return
        self._next_check = now + POLL_INTERVAL_SECONDS
        if self._redis.exists(self._key):
            raise DownloadCancelled("cancelled by user")

    @staticmethod
    def request_cancel(job_id: str, redis_client, ttl: int = 3600) -> None:
        redis_client.set(f"job:{job_id}:cancel", "1", ex=ttl)

    @staticmethod
    def clear(job_id: str, redis_client) -> None:
        redis_client.delete(f"job:{job_id}:cancel")
