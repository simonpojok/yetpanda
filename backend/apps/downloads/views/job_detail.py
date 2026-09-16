"""GET/DELETE /v1/jobs/{id}"""

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import DownloadJob
from ..serializers.job_serializer import JobSerializer
from ..services.job_cancellation import JobCancellationService
from ..services.progress_reader import ProgressReader


class JobDetailView(APIView):
    def get(self, request, job_id):
        job = self._get(request, job_id)
        progress = ProgressReader().for_jobs([job])
        return Response(JobSerializer(job, context={"progress": progress}).data)

    def delete(self, request, job_id):
        job = self._get(request, job_id)
        JobCancellationService().cancel_job(job)
        job.refresh_from_db()
        return Response(JobSerializer(job).data)

    def _get(self, request, job_id) -> DownloadJob:
        # Scoping by session is the authorisation boundary; the signed cookie
        # is what makes it one.
        return get_object_or_404(
            DownloadJob, pk=job_id, session_id=request.anon_session_id
        )
