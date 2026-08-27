"""Coalesces yt-dlp's progress firehose into something a database survives.

Progress hooks fire hundreds of times a second on a fast fragmented
download. Writing each one to Postgres would mean WAL amplification, dead
tuple churn and lock contention with the dispatcher on the same table. So
live progress goes to Redis (~2.5 writes/sec/job) and Postgres sees only
stage transitions, terminal states, and a 5-second heartbeat.
"""

import json
import time

import redis
from django.conf import settings
from django.utils import timezone

from ..models import DownloadJob, JobStage

EMIT_INTERVAL_SECONDS = 0.4
EMIT_BYTE_DELTA = 2 * 1024 * 1024  # so slow links still tick
DB_INTERVAL_SECONDS = 5.0
PROGRESS_TTL_SECONDS = 3600

# A merged MP4 runs two full 0-100% download passes, then postprocesses. A
# naive percent appears to reset halfway, so weight the phases instead.
WEIGHTS_MERGED = {"video": 0.55, "audio": 0.20, "post": 0.25}
WEIGHTS_AUDIO_ONLY = {"video": 0.0, "audio": 0.70, "post": 0.30}


def get_redis() -> redis.Redis:
    return redis.Redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)


class ProgressReporter:
    def __init__(self, job_id: str, redis_client=None, merged: bool = True) -> None:
        self.job_id = str(job_id)
        self._redis = redis_client or get_redis()
        self._weights = WEIGHTS_MERGED if merged else WEIGHTS_AUDIO_ONLY
        self._stage: str | None = None
        self._last_emit = 0.0
        self._last_bytes = 0
        self._last_db = 0.0
        self._video_done = False

    # ------------------------------------------------------------------ emit
    def emit(
        self,
        *,
        stage: JobStage,
        stage_percent: float | None = None,
        downloaded: int = 0,
        total: int | None = None,
        speed: float | None = None,
        eta: int | None = None,
        fragment: tuple | None = None,
        terminal: bool = False,
    ) -> None:
        if not self._should_emit(stage, downloaded, terminal):
            return

        overall = self._overall_percent(stage, stage_percent)
        payload = {
            "job_id": self.job_id,
            "stage": str(stage),
            "stage_label": JobStage(stage).label,
            "percent": round(overall, 2),
            "stage_percent": round(stage_percent, 2) if stage_percent is not None else None,
            "downloaded_bytes": downloaded,
            "total_bytes": total,
            "speed_bps": int(speed) if speed else None,
            "eta_seconds": eta,
            "fragment_index": fragment[0] if fragment else None,
            "fragment_count": fragment[1] if fragment else None,
            "updated_at": timezone.now().isoformat(),
        }

        pipe = self._redis.pipeline(transaction=False)
        pipe.set(self._key, json.dumps(payload), ex=PROGRESS_TTL_SECONDS)
        pipe.execute()

        self._stage = str(stage)
        self._last_emit = time.monotonic()
        self._last_bytes = downloaded

        now = time.monotonic()
        if terminal or now - self._last_db >= DB_INTERVAL_SECONDS:
            DownloadJob.objects.filter(pk=self.job_id).update(
                stage=stage,
                progress_percent=overall,
                downloaded_bytes=downloaded,
                est_total_bytes=total,
                heartbeat_at=timezone.now(),
            )
            self._last_db = now

    def heartbeat(self) -> None:
        DownloadJob.objects.filter(pk=self.job_id).update(heartbeat_at=timezone.now())

    # ------------------------------------------------------------- internals
    @property
    def _key(self) -> str:
        return f"job:{self.job_id}:progress"

    def _should_emit(self, stage: JobStage, downloaded: int, terminal: bool) -> bool:
        if terminal or str(stage) != self._stage:
            return True
        now = time.monotonic()
        return (
            now - self._last_emit >= EMIT_INTERVAL_SECONDS
            or downloaded - self._last_bytes >= EMIT_BYTE_DELTA
        )

    def _overall_percent(self, stage: JobStage, stage_percent: float | None) -> float:
        """Map a within-stage percent onto the whole job, monotonically."""
        fraction = (stage_percent or 0) / 100.0
        w = self._weights

        if stage == JobStage.DOWNLOADING_VIDEO:
            return w["video"] * fraction * 100
        if stage == JobStage.DOWNLOADING_AUDIO:
            self._video_done = self._video_done or w["video"] > 0
            return (w["video"] + w["audio"] * fraction) * 100
        if stage in (JobStage.PENDING, JobStage.RESOLVING):
            return 0.0
        if stage in (JobStage.DONE, JobStage.FAILED):
            return 100.0
        # Any postprocessing stage sits in the final band.
        return (w["video"] + w["audio"] + w["post"] * 0.5) * 100
