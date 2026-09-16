"""Cancel a job or a whole batch."""

import logging

from django.db import transaction
from django.utils import timezone

from ..hooks.cancellation_sentinel import CancellationSentinel
from ..models import (
    ACTIVE_JOB_STATUSES,
    BatchStatus,
    DownloadBatch,
    DownloadJob,
    JobStatus,
)
from .progress_reporter import get_redis

logger = logging.getLogger(__name__)


class JobCancellationService:
    def __init__(self, redis_client=None) -> None:
        self._redis = redis_client or get_redis()

    def cancel_job(self, job: DownloadJob) -> bool:
        if job.is_terminal:
            return False

        # A queued job is only a Postgres row - no Celery message exists yet,
        # so cancelling it is one UPDATE with no revoke and no ghost task.
        if job.status == JobStatus.QUEUED:
            DownloadJob.objects.filter(pk=job.pk, status=JobStatus.QUEUED).update(
                status=JobStatus.CANCELLED, finished_at=timezone.now()
            )
            return True

        CancellationSentinel.request_cancel(str(job.id), self._redis)
        DownloadJob.objects.filter(pk=job.pk).update(status=JobStatus.CANCELLED)
        if job.celery_task_id:
            self._revoke(job.celery_task_id)
        return True

    def cancel_batch(self, batch: DownloadBatch) -> int:
        with transaction.atomic():
            queued = list(
                DownloadJob.objects.filter(
                    batch=batch, status=JobStatus.QUEUED
                ).values_list("id", flat=True)
            )
            DownloadJob.objects.filter(id__in=queued).update(
                status=JobStatus.CANCELLED, finished_at=timezone.now()
            )

        active = DownloadJob.objects.filter(batch=batch, status__in=ACTIVE_JOB_STATUSES)
        for job in active:
            self.cancel_job(job)

        DownloadBatch.objects.filter(pk=batch.pk).update(
            status=BatchStatus.CANCELLED, completed_at=timezone.now()
        )
        return len(queued) + active.count()

    def _revoke(self, task_id: str) -> None:
        from config.celery import app

        try:
            app.control.revoke(task_id, terminate=True, signal="SIGTERM")
        except Exception:  # noqa: BLE001 - best effort; the sentinel is primary
            logger.warning("could not revoke task %s", task_id)
