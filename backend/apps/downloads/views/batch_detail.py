"""GET/DELETE /v1/batches/{id} and POST /v1/batches/{id}/retry"""

from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.extraction.domain.error_code import RETRYABLE

from ..models import ACTIVE_JOB_STATUSES, BatchStatus, DownloadBatch, DownloadJob, JobStatus
from ..serializers.batch_serializer import BatchSerializer
from ..services.job_cancellation import JobCancellationService
from ..services.progress_reader import ProgressReader

MAX_ATTEMPTS = 3


class BatchDetailView(APIView):
    def get(self, request, batch_id):
        batch = self._get(request, batch_id)
        active = [j for j in batch.items.all() if j.status in ACTIVE_JOB_STATUSES]
        progress = ProgressReader().for_jobs(active)
        return Response(BatchSerializer(batch, context={"progress": progress}).data)

    def delete(self, request, batch_id):
        batch = self._get(request, batch_id)
        JobCancellationService().cancel_batch(batch)
        batch.refresh_from_db()
        return Response(BatchSerializer(batch).data)

    def _get(self, request, batch_id) -> DownloadBatch:
        return get_object_or_404(
            DownloadBatch, pk=batch_id, session_id=request.anon_session_id
        )


class BatchRetryView(APIView):
    """Retry only the children that can actually succeed on a second attempt.

    Retrying members_only or geo_blocked is pure waste and looks like abuse to
    YouTube, so those stay failed and the response says how many were skipped.
    """

    def post(self, request, batch_id):
        batch = get_object_or_404(
            DownloadBatch, pk=batch_id, session_id=request.anon_session_id
        )

        failed = DownloadJob.objects.filter(batch=batch, status=JobStatus.FAILED)
        retryable_ids = [
            job.id
            for job in failed
            if job.error_code in {str(c) for c in RETRYABLE}
            and job.attempts < MAX_ATTEMPTS
        ]
        skipped = failed.count() - len(retryable_ids)

        if retryable_ids:
            DownloadJob.objects.filter(id__in=retryable_ids).update(
                status=JobStatus.QUEUED,
                stage="pending",
                error_code="",
                error_message="",
                error_detail=None,
                attempts=F("attempts") + 1,
                not_before=timezone.now(),
                progress_percent=0,
                downloaded_bytes=0,
                finished_at=None,
            )
            DownloadBatch.objects.filter(pk=batch.pk).update(
                failed_items=F("failed_items") - len(retryable_ids),
                status=BatchStatus.RUNNING,
                completed_at=None,
            )

        return Response({"retrying": len(retryable_ids), "skipped": skipped})
