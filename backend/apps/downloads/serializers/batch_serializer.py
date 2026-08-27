"""Batch representation.

Full detail is sent only for children that are still running; everything else
gets a one-line summary. With a concurrency of 4 that is a handful of detailed
objects no matter how large the batch, so a 200-item playlist still polls in
a couple of kilobytes.
"""

from rest_framework import serializers

from ..models import ACTIVE_JOB_STATUSES, BatchStatus, DownloadBatch
from .job_serializer import JobSerializer


class BatchSerializer(serializers.ModelSerializer):
    rollup = serializers.SerializerMethodField()
    active = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    archive = serializers.SerializerMethodField()

    class Meta:
        model = DownloadBatch
        fields = (
            "id",
            "source_url",
            "title",
            "kind",
            "preference",
            "status",
            "created_at",
            "completed_at",
            "expires_at",
            "rollup",
            "active",
            "items",
            "archive",
        )

    def get_rollup(self, batch: DownloadBatch) -> dict:
        return {
            "total": batch.total_items,
            "succeeded": batch.succeeded_items,
            "failed": batch.failed_items,
            "cancelled": batch.cancelled_items,
            "finished": batch.finished_items,
            "percent": self._percent(batch),
            "bytes_done": batch.actual_bytes,
            "bytes_total_estimate": batch.est_total_bytes,
        }

    def _percent(self, batch: DownloadBatch) -> float:
        """Byte-weighted, not item-weighted.

        Item-weighted percent lurches badly when a playlist mixes two-minute
        and two-hour videos.
        """
        if batch.est_total_bytes:
            return round(min(100.0, 100 * batch.actual_bytes / batch.est_total_bytes), 2)
        if batch.total_items:
            return round(100 * batch.finished_items / batch.total_items, 2)
        return 0.0

    def get_active(self, batch: DownloadBatch) -> list[dict]:
        children = [j for j in self._children(batch) if j.status in ACTIVE_JOB_STATUSES]
        return JobSerializer(children, many=True, context=self.context).data

    def get_items(self, batch: DownloadBatch) -> list[dict]:
        from ..services.file_signer import FileSigner

        signer = FileSigner()
        rows = []
        for job in self._children(batch):
            row = {
                "index": job.batch_index,
                "id": str(job.id),
                "video_id": job.video_id,
                "title": job.title,
                "duration": job.duration,
                "status": job.status,
                "size_bytes": job.size_bytes,
            }
            if job.status == "succeeded" and job.relative_path:
                row["download_url"] = signer.build_url(
                    str(job.id), job.output_filename, attachment=True
                )
            if job.error_code:
                row["error"] = {"code": job.error_code, "message": job.error_message}
            rows.append(row)
        return rows

    def get_archive(self, batch: DownloadBatch) -> dict:
        """ZIP is offered only for batches small enough to stream cheaply."""
        from django.conf import settings

        eligible = (
            batch.status
            in (BatchStatus.COMPLETED, BatchStatus.COMPLETED_WITH_ERRORS)
            and batch.succeeded_items > 0
            and batch.total_items <= settings.ZIP_MAX_ITEMS
            and batch.actual_bytes <= settings.ZIP_MAX_BYTES
        )
        return {
            "available": eligible,
            "url": f"/v1/batches/{batch.id}/archive.zip" if eligible else None,
            "reason": None if eligible else self._archive_reason(batch),
        }

    def _archive_reason(self, batch: DownloadBatch) -> str | None:
        from django.conf import settings

        if not batch.is_terminal:
            return "Available once the batch finishes."
        if batch.succeeded_items == 0:
            return "Nothing finished downloading."
        if batch.total_items > settings.ZIP_MAX_ITEMS:
            return "Too many items for one archive. Download files individually."
        if batch.actual_bytes > settings.ZIP_MAX_BYTES:
            return "Too large for one archive. Download files individually."
        return None

    def _children(self, batch: DownloadBatch):
        if not hasattr(batch, "_cached_children"):
            batch._cached_children = list(batch.items.order_by("batch_index"))
        return batch._cached_children
