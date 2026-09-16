"""Decides which queued jobs actually reach Celery, and when."""

import logging
from functools import partial
from uuid import UUID

from django.db import connection, transaction
from django.utils import timezone

from ..models import DownloadJob, JobStatus
from ..services.disk_guard import DiskGuard, DiskState
from .ready_job_query import SELECT_READY_JOBS
from .session_quota import SessionQuota

logger = logging.getLogger(__name__)

# Serialises dispatch across every Beat instance and machine.
DISPATCH_LOCK_ID = 0x59455450  # "YETP"


class FairDispatcher:
    def __init__(self) -> None:
        self.quota = SessionQuota()
        self.disk = DiskGuard()

    def dispatch(self) -> int:
        """Claim ready jobs and hand them to Celery. Returns how many."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_try_advisory_lock(%s)", [DISPATCH_LOCK_ID])
            if not cursor.fetchone()[0]:
                return 0  # another dispatcher is mid-round
            try:
                return self._dispatch(cursor)
            finally:
                cursor.execute("SELECT pg_advisory_unlock(%s)", [DISPATCH_LOCK_ID])

    def _dispatch(self, cursor) -> int:
        capacity = self._capacity()
        if capacity <= 0:
            return 0

        cursor.execute(
            SELECT_READY_JOBS,
            {
                "per_session_slots": self.quota.per_session_slots,
                "capacity": capacity,
            },
        )
        candidate_ids = [row[0] for row in cursor.fetchall()]
        if not candidate_ids:
            return 0

        claimed = self._claim(candidate_ids)
        logger.info("dispatched %s job(s)", len(claimed))
        return len(claimed)

    def _capacity(self) -> int:
        """Free slots right now, shrunk or zeroed by disk pressure."""
        state = self.disk.state()
        if state is DiskState.CRITICAL:
            # Pause dispatch rather than failing jobs: queued children cost
            # nothing and resume by themselves once eviction frees space.
            logger.warning("disk critical - dispatch paused")
            return 0

        limit = self.quota.global_slots
        if state is DiskState.HIGH:
            limit = max(1, limit // 2)

        running = DownloadJob.objects.filter(
            status__in=[JobStatus.DISPATCHED, JobStatus.RUNNING]
        ).count()
        return limit - running

    def _claim(self, candidate_ids: list[UUID]) -> list[UUID]:
        """Compare-and-set the claim so two dispatchers cannot double-send."""
        from ..tasks.run_download import run_download

        with transaction.atomic():
            claimed = list(
                DownloadJob.objects.filter(
                    id__in=candidate_ids, status=JobStatus.QUEUED
                )
                .select_for_update(skip_locked=True)
                .values_list("id", flat=True)
            )
            if not claimed:
                return []

            now = timezone.now()
            DownloadJob.objects.filter(id__in=claimed).update(
                status=JobStatus.DISPATCHED, dispatched_at=now, heartbeat_at=now
            )
            for job_id in claimed:
                transaction.on_commit(
                    partial(run_download.apply_async, args=[str(job_id)], queue="download")
                )
        return claimed
