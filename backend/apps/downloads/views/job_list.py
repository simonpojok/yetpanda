"""GET /v1/jobs?ids= - the polling hot path.

One request covers every job the client is watching. Polling per job would
multiply request count by batch size, which is exactly what makes naive
implementations fall over on a 50-item playlist.
"""

from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import DownloadJob
from ..serializers.job_serializer import JobSerializer
from ..services.progress_reader import ProgressReader

MAX_IDS = 200


class JobListView(APIView):
    def get(self, request):
        raw_ids = (request.query_params.get("ids") or "").strip()
        if not raw_ids:
            return Response({"jobs": []})

        ids = [value for value in raw_ids.split(",") if value][:MAX_IDS]
        jobs = list(
            DownloadJob.objects.filter(
                id__in=ids, session_id=request.anon_session_id
            ).order_by("created_at")
        )

        progress = ProgressReader().for_jobs(jobs)
        data = JobSerializer(jobs, many=True, context={"progress": progress}).data
        return Response({"jobs": data})
