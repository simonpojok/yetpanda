"""The task that actually fetches a file.

Cancellation is layered here on purpose. The progress hook handles the common
case, but postprocessor hooks only fire at start and finish - so a six-minute
transcode is a blind spot. SIGTERM covers that, and the handler reaps ffmpeg
*grandchildren*, which would otherwise be orphaned and keep running while
holding the temp file open.
"""

import logging
import shutil
import signal
from contextlib import contextmanager
from pathlib import Path

import psutil
from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from yt_dlp.utils import DownloadCancelled

from apps.extraction.domain.error_code import ErrorCode
from apps.extraction.domain.exceptions import ExtractionError
from apps.extraction.services.ytdlp_client import YtDlpClient

from ..downloaders.factory import DownloaderFactory
from ..hooks.cancellation_sentinel import CancellationSentinel
from ..hooks.stage_mapper import (
    stage_for_download,
    stage_for_postprocessor,
    total_bytes_from,
)
from ..models import DownloadJob, JobStage, JobStatus, SubtitleAsset
from ..services.disk_guard import DiskGuard
from ..services.progress_reporter import ProgressReporter, get_redis
from ..storage.local_disk_storage import LocalDiskStorage

logger = logging.getLogger(__name__)


@contextmanager
def reap_children_on_sigterm():
    """Kill ffmpeg and friends before we go, then abort cleanly."""

    def handler(signum, frame):
        current = psutil.Process()
        children = current.children(recursive=True)
        for child in children:
            child.terminate()
        _, still_alive = psutil.wait_procs(children, timeout=5)
        for child in still_alive:
            child.kill()
        raise DownloadCancelled("terminated by worker shutdown or revoke")

    previous = signal.signal(signal.SIGTERM, handler)
    try:
        yield
    finally:
        signal.signal(signal.SIGTERM, previous)


@shared_task(name="downloads.run_download", bind=True, ignore_result=True)
def run_download(self, job_id: str) -> str:
    job = DownloadJob.objects.filter(pk=job_id).first()
    if job is None or job.status not in (JobStatus.DISPATCHED, JobStatus.QUEUED):
        return "skipped"

    storage = LocalDiskStorage()
    work_dir = storage.work_dir(str(job.id))
    redis_client = get_redis()
    reporter = ProgressReporter(
        str(job.id), redis_client, merged=job.kind == "video"
    )
    sentinel = CancellationSentinel(str(job.id), redis_client)

    DownloadJob.objects.filter(pk=job.pk).update(
        status=JobStatus.RUNNING,
        stage=JobStage.RESOLVING,
        started_at=timezone.now(),
        heartbeat_at=timezone.now(),
        celery_task_id=self.request.id or "",
        worker_name=self.request.hostname or "",
    )

    try:
        if not DiskGuard().has_room_for(job.est_total_bytes or 0):
            raise ExtractionError(ErrorCode.DISK_FULL, "insufficient free space")

        with reap_children_on_sigterm():
            result = _execute(job, work_dir, reporter, sentinel)

        relative_path = storage.finalize(work_dir, str(job.id), result.filename)
        _record_subtitles(job, storage, work_dir, result)

        reporter.emit(stage=JobStage.DONE, stage_percent=100, terminal=True)
        _mark_succeeded(job, result, relative_path)
        return "succeeded"

    except DownloadCancelled:
        _mark_terminal(job, JobStatus.CANCELLED, ErrorCode.CANCELLED, "Download cancelled.")
        return "cancelled"
    except ExtractionError as exc:
        # Defence in depth: whatever route a cancellation arrives by, it must
        # not be recorded as a failure.
        if exc.code is ErrorCode.CANCELLED:
            _mark_terminal(
                job, JobStatus.CANCELLED, ErrorCode.CANCELLED, "Download cancelled."
            )
            return "cancelled"
        _mark_terminal(job, JobStatus.FAILED, exc.code, exc.message, exc.detail)
        return "failed"
    except Exception as exc:  # noqa: BLE001 - last resort, never leak upward
        logger.exception("job %s crashed", job_id)
        _mark_terminal(
            job, JobStatus.FAILED, ErrorCode.UNKNOWN, "Something went wrong.", str(exc)
        )
        return "failed"
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
        CancellationSentinel.clear(str(job.id), redis_client)
        _roll_up_batch(job)


def _execute(job: DownloadJob, work_dir: Path, reporter, sentinel):
    client = YtDlpClient()

    def progress_hook(status: dict) -> None:
        sentinel.check()
        if status.get("status") != "downloading":
            return
        # The hook dict is mutated and reused across calls, so read now.
        info = status.get("info_dict") or {}
        total = total_bytes_from(status)
        downloaded = status.get("downloaded_bytes", 0)
        reporter.emit(
            stage=stage_for_download(info),
            stage_percent=(100 * downloaded / total) if total else None,
            downloaded=downloaded,
            total=total,
            speed=status.get("speed"),
            eta=status.get("eta"),
            fragment=(status.get("fragment_index"), status.get("fragment_count")),
        )

    def postprocessor_hook(status: dict) -> None:
        sentinel.check()
        reporter.emit(stage=stage_for_postprocessor(status.get("postprocessor", "")))

    downloader = DownloaderFactory().for_job(
        job.kind,
        job.spec or {},
        client,
        {"progress_hooks": [progress_hook], "postprocessor_hooks": [postprocessor_hook]},
    )
    return downloader.download(job.source_url, job.spec or {}, work_dir)


def _record_subtitles(job, storage, work_dir: Path, result) -> None:
    for name in result.subtitle_files:
        source = work_dir / name
        if not source.exists():
            continue
        relative = storage.finalize(work_dir, str(job.id), name)
        parts = name.rsplit(".", 2)
        SubtitleAsset.objects.update_or_create(
            job=job,
            lang=parts[-2] if len(parts) >= 3 else "und",
            fmt=parts[-1],
            is_auto=False,
            defaults={
                "relative_path": relative,
                "size_bytes": storage.size_of(relative),
            },
        )


def _mark_succeeded(job, result, relative_path: str) -> None:
    now = timezone.now()
    DownloadJob.objects.filter(pk=job.pk).update(
        status=JobStatus.SUCCEEDED,
        stage=JobStage.DONE,
        progress_percent=100,
        output_filename=result.filename,
        relative_path=relative_path,
        content_type=result.content_type,
        size_bytes=result.size_bytes,
        finished_at=now,
        heartbeat_at=now,
        expires_at=now + timezone.timedelta(seconds=settings.JOB_TTL_SECONDS),
    )


def _mark_terminal(job, status, code, message: str, detail: str = "") -> None:
    DownloadJob.objects.filter(pk=job.pk).update(
        status=status,
        stage=JobStage.FAILED if status == JobStatus.FAILED else job.stage,
        error_code=str(code),
        error_message=message,
        error_detail={"detail": detail[:4000]} if detail else None,
        finished_at=timezone.now(),
    )


def _roll_up_batch(job) -> None:
    """Update parent counters with F() so concurrent children cannot race."""
    if job.batch_id is None:
        return

    fresh = DownloadJob.objects.filter(pk=job.pk).values("status", "size_bytes").first()
    if not fresh:
        return

    from ..models import DownloadBatch
    from ..services.batch_finalizer import BatchFinalizer

    status = fresh["status"]
    updates = {}
    if status == JobStatus.SUCCEEDED:
        updates["succeeded_items"] = F("succeeded_items") + 1
        updates["actual_bytes"] = F("actual_bytes") + (fresh["size_bytes"] or 0)
    elif status == JobStatus.FAILED:
        updates["failed_items"] = F("failed_items") + 1
    elif status == JobStatus.CANCELLED:
        updates["cancelled_items"] = F("cancelled_items") + 1
    else:
        return

    with transaction.atomic():
        DownloadBatch.objects.filter(pk=job.batch_id).update(**updates)
    BatchFinalizer().maybe_finalize(job.batch_id)
