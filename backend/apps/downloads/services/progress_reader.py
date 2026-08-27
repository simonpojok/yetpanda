"""Reads live progress for the API, preferring Redis over the database."""

import json

from ..models import DownloadJob
from .progress_reporter import get_redis


class ProgressReader:
    def __init__(self, redis_client=None) -> None:
        self._redis = redis_client or get_redis()

    def for_jobs(self, jobs: list[DownloadJob]) -> dict[str, dict]:
        """One pipelined round-trip for every job the client is watching."""
        if not jobs:
            return {}

        pipe = self._redis.pipeline(transaction=False)
        for job in jobs:
            pipe.get(f"job:{job.id}:progress")
        raw_values = pipe.execute()

        result: dict[str, dict] = {}
        for job, raw in zip(jobs, raw_values, strict=True):
            result[str(job.id)] = self._parse(raw) or self._from_row(job)
        return result

    def _parse(self, raw: str | None) -> dict | None:
        if not raw:
            return None
        try:
            return json.loads(raw)
        except (ValueError, TypeError):
            return None

    def _from_row(self, job: DownloadJob) -> dict:
        """Fallback for queued jobs and anything Redis has already expired."""
        return {
            "job_id": str(job.id),
            "stage": job.stage,
            "stage_label": job.get_stage_display(),
            "percent": job.progress_percent,
            "stage_percent": None,
            "downloaded_bytes": job.downloaded_bytes,
            "total_bytes": job.est_total_bytes,
            "speed_bps": None,
            "eta_seconds": None,
            "fragment_index": None,
            "fragment_count": None,
        }
