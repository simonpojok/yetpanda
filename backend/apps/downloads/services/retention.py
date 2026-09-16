"""Everything that deletes things on a schedule."""

import logging
import shutil
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.db.models import F
from django.utils import timezone

from apps.extraction.domain.error_code import ErrorCode

from ..models import DownloadJob, JobStatus, ProbeCache, Session

logger = logging.getLogger(__name__)

STALE_HEARTBEAT_SECONDS = 180
MAX_ATTEMPTS = 3
ORPHAN_MIN_AGE_SECONDS = 1800


class RetentionService:
    def expire_finished_files(self) -> int:
        """Delete files past their TTL.

        The file goes first and the row second. The reverse order leaks disk
        if we crash between the two; sweep_orphan_dirs is the safety net for
        the direction we chose.
        """
        now = timezone.now()
        expired = DownloadJob.objects.filter(
            status=JobStatus.SUCCEEDED, expires_at__lte=now
        ).only("id")

        count = 0
        for job in expired.iterator(chunk_size=200):
            self._remove_dir(Path(settings.MEDIA_DONE_ROOT) / str(job.id))
            DownloadJob.objects.filter(pk=job.pk).update(
                status=JobStatus.EXPIRED, relative_path="", size_bytes=None
            )
            count += 1
        if count:
            logger.info("expired %s finished file(s)", count)
        return count

    def reap_stale_jobs(self) -> int:
        """Recover jobs whose worker died without updating them.

        Nothing in-process can do this - SIGKILL, OOM and machine loss leave
        no chance to run a handler - so the heartbeat is the only signal.
        """
        cutoff = timezone.now() - timedelta(seconds=STALE_HEARTBEAT_SECONDS)
        stale = DownloadJob.objects.filter(
            status__in=[JobStatus.DISPATCHED, JobStatus.RUNNING],
            heartbeat_at__lt=cutoff,
        )

        count = 0
        for job in stale.iterator(chunk_size=100):
            self._remove_dir(Path(settings.MEDIA_WORK_ROOT) / str(job.id))
            if job.attempts + 1 < MAX_ATTEMPTS:
                DownloadJob.objects.filter(pk=job.pk).update(
                    status=JobStatus.QUEUED,
                    attempts=F("attempts") + 1,
                    heartbeat_at=None,
                    celery_task_id="",
                    not_before=timezone.now(),
                )
            else:
                DownloadJob.objects.filter(pk=job.pk).update(
                    status=JobStatus.FAILED,
                    attempts=F("attempts") + 1,
                    error_code=str(ErrorCode.WORKER_LOST),
                    error_message="That download was interrupted. Try again.",
                    finished_at=timezone.now(),
                )
            count += 1
        if count:
            logger.warning("reaped %s stale job(s)", count)
        return count

    def sweep_orphan_dirs(self) -> int:
        """Delete work/done directories with no live row behind them."""
        cutoff = timezone.now() - timedelta(seconds=ORPHAN_MIN_AGE_SECONDS)
        count = 0
        for root, live_statuses in (
            (Path(settings.MEDIA_WORK_ROOT), [JobStatus.DISPATCHED, JobStatus.RUNNING]),
            (Path(settings.MEDIA_DONE_ROOT), [JobStatus.SUCCEEDED]),
        ):
            if not root.exists():
                continue
            for entry in root.iterdir():
                if not entry.is_dir():
                    continue
                mtime = timezone.datetime.fromtimestamp(
                    entry.stat().st_mtime, tz=timezone.get_current_timezone()
                )
                if mtime > cutoff:
                    continue
                if DownloadJob.objects.filter(
                    id=entry.name, status__in=live_statuses
                ).exists():
                    continue
                self._remove_dir(entry)
                count += 1
        if count:
            logger.info("swept %s orphan dir(s)", count)
        return count

    def purge_old_rows(self) -> int:
        cutoff = timezone.now() - timedelta(days=settings.ROW_RETENTION_DAYS)
        jobs, _ = DownloadJob.objects.filter(finished_at__lt=cutoff).delete()
        probes, _ = ProbeCache.objects.filter(expires_at__lt=cutoff).delete()
        sessions, _ = Session.objects.filter(last_seen_at__lt=cutoff).delete()
        return jobs + probes + sessions

    def _remove_dir(self, path: Path) -> None:
        if not str(path).startswith(str(settings.MEDIA_ROOT)):
            raise ValueError(f"refusing to delete outside MEDIA_ROOT: {path}")
        shutil.rmtree(path, ignore_errors=True)
