"""One downloadable file. A batch item and a single download are the same thing."""

import uuid

from django.db import models
from django.db.models import Q
from django.utils import timezone

from .enums import JobStage, JobStatus, MediaKindChoice, SubtitleModeChoice


class DownloadJob(models.Model):
    """The unit of work.

    A batch child and a standalone download run through the identical task
    with the identical spec; the only differences are ``priority`` and the
    presence of ``batch``. That keeps one download code path, and lets a batch
    item be cancelled, retried or played exactly like a single.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        "downloads.Session", on_delete=models.CASCADE, related_name="jobs"
    )
    batch = models.ForeignKey(
        "downloads.DownloadBatch",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="items",
    )
    batch_index = models.IntegerField(null=True, blank=True)
    client_ip_hash = models.CharField(max_length=32, blank=True, db_index=True)

    source_url = models.TextField(help_text="Canonicalised - never raw user input.")
    video_id = models.CharField(max_length=32, db_index=True)
    title = models.TextField(blank=True)
    channel = models.TextField(blank=True)
    duration = models.IntegerField(null=True, blank=True)
    thumbnail_url = models.TextField(blank=True)

    kind = models.CharField(max_length=8, choices=MediaKindChoice.choices)
    spec = models.JSONField(help_text="Container, height, bitrate, format selector, subs.")
    subtitle_mode = models.CharField(
        max_length=16, choices=SubtitleModeChoice.choices, default=SubtitleModeChoice.NONE
    )
    subtitle_langs = models.JSONField(default=list, blank=True)

    status = models.CharField(
        max_length=16, choices=JobStatus.choices, default=JobStatus.QUEUED
    )
    stage = models.CharField(max_length=24, choices=JobStage.choices, default=JobStage.PENDING)
    priority = models.SmallIntegerField(default=0, help_text="10 = single, 0 = batch item.")
    attempts = models.SmallIntegerField(default=0)
    celery_task_id = models.CharField(max_length=64, blank=True, db_index=True)
    worker_name = models.CharField(max_length=128, blank=True)

    progress_percent = models.FloatField(default=0)
    downloaded_bytes = models.BigIntegerField(default=0)
    est_total_bytes = models.BigIntegerField(null=True, blank=True)

    output_filename = models.TextField(blank=True)
    relative_path = models.TextField(blank=True, help_text="Relative to MEDIA_DONE_ROOT.")
    content_type = models.CharField(max_length=64, blank=True)
    size_bytes = models.BigIntegerField(null=True, blank=True)

    error_code = models.CharField(max_length=32, blank=True, db_index=True)
    error_message = models.TextField(blank=True)
    error_detail = models.JSONField(null=True, blank=True, help_text="Internal only.")

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    not_before = models.DateTimeField(default=timezone.now)
    dispatched_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    heartbeat_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        indexes = [
            # The dispatcher runs every second forever, against a table that
            # will accumulate millions of dead rows. Partial indexes keep the
            # working set tiny and cache-resident regardless of history size.
            models.Index(
                fields=["priority", "created_at"],
                name="ix_job_dispatch",
                condition=Q(status="queued"),
            ),
            models.Index(
                fields=["session", "status"],
                name="ix_job_session_active",
                condition=Q(status__in=["dispatched", "running"]),
            ),
            models.Index(
                fields=["heartbeat_at"],
                name="ix_job_reaper",
                condition=Q(status__in=["dispatched", "running"]),
            ),
            models.Index(
                fields=["expires_at"],
                name="ix_job_expiry",
                condition=Q(status="succeeded"),
            ),
            models.Index(fields=["batch", "batch_index"], name="ix_job_batch_order"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["batch", "batch_index"],
                name="uq_job_batch_index",
                condition=Q(batch__isnull=False),
            )
        ]

    def __str__(self) -> str:
        return f"{self.kind} {self.video_id} [{self.status}]"

    @property
    def is_terminal(self) -> bool:
        return self.status in {
            JobStatus.SUCCEEDED,
            JobStatus.FAILED,
            JobStatus.CANCELLED,
            JobStatus.SKIPPED,
            JobStatus.EXPIRED,
        }
