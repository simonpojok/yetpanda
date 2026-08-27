"""Decides when a batch is done, and whether it counts as a success."""

import logging

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from ..models import BatchStatus, DownloadBatch

logger = logging.getLogger(__name__)


class BatchFinalizer:
    def maybe_finalize(self, batch_id) -> bool:
        """Runs once per child completion, so select_for_update is cheap here."""
        with transaction.atomic():
            batch = (
                DownloadBatch.objects.select_for_update().filter(pk=batch_id).first()
            )
            if batch is None or batch.is_terminal:
                return False

            if batch.finished_items < batch.total_items:
                if batch.status == BatchStatus.PENDING:
                    batch.status = BatchStatus.RUNNING
                    batch.save(update_fields=["status"])
                return False

            batch.status = self._final_status(batch)
            batch.completed_at = timezone.now()
            batch.expires_at = batch.completed_at + timezone.timedelta(
                seconds=settings.BATCH_TTL_SECONDS
            )
            batch.save(update_fields=["status", "completed_at", "expires_at"])
            logger.info("batch %s finished as %s", batch.id, batch.status)
            return True

    def _final_status(self, batch: DownloadBatch) -> str:
        """One bad item must not sink an otherwise successful batch."""
        if batch.cancelled_items and not batch.succeeded_items:
            return BatchStatus.CANCELLED
        if batch.succeeded_items == 0:
            return BatchStatus.FAILED
        if batch.failed_items or batch.cancelled_items:
            return BatchStatus.COMPLETED_WITH_ERRORS
        return BatchStatus.COMPLETED
