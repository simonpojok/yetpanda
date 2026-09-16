"""A bulk playlist download: one format preference across many items."""

import uuid

from django.db import models

from .enums import BatchStatus, MediaKindChoice


class DownloadBatch(models.Model):
    """Parent of many :class:`DownloadJob` children.

    The counters are materialised here rather than recomputed with a
    ``GROUP BY`` on every poll: a 200-item batch polled once a second by
    several open tabs would otherwise scan the child table constantly.
    Children update them with ``F()`` expressions, so concurrent workers on
    different machines cannot race.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        "downloads.Session", on_delete=models.CASCADE, related_name="batches"
    )
    client_ip_hash = models.CharField(max_length=32, blank=True, db_index=True)
    source_url = models.TextField()
    playlist_id = models.CharField(max_length=64, blank=True, db_index=True)
    title = models.TextField(blank=True)

    kind = models.CharField(max_length=8, choices=MediaKindChoice.choices)
    preference = models.JSONField(help_text="Format spec applied to every child.")

    status = models.CharField(
        max_length=24, choices=BatchStatus.choices, default=BatchStatus.PENDING, db_index=True
    )

    total_items = models.IntegerField(default=0)
    succeeded_items = models.IntegerField(default=0)
    failed_items = models.IntegerField(default=0)
    cancelled_items = models.IntegerField(default=0)

    est_total_bytes = models.BigIntegerField(default=0)
    actual_bytes = models.BigIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [models.Index(fields=["session", "-created_at"], name="ix_batch_session")]

    def __str__(self) -> str:
        return f"Batch {self.id} ({self.succeeded_items}/{self.total_items})"

    @property
    def finished_items(self) -> int:
        return self.succeeded_items + self.failed_items + self.cancelled_items

    @property
    def is_terminal(self) -> bool:
        return self.status in {
            BatchStatus.COMPLETED,
            BatchStatus.COMPLETED_WITH_ERRORS,
            BatchStatus.FAILED,
            BatchStatus.CANCELLED,
        }
