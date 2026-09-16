"""GET /v1/files/{job_id}/{token}/{filename}

In production the proxy serves the bytes: Django returns an empty body naming
the path, and Caddy's file_server handles Range/206 natively, so a multi-GB
file never occupies a worker. The in-process path is the dev fallback.
"""

from django.conf import settings
from django.http import Http404, HttpResponse
from django.views import View

from ..models import DownloadJob, JobStatus
from ..http.ranged_response import ranged_file_response
from ..services.file_signer import FileSigner
from ..storage.local_disk_storage import LocalDiskStorage


class FileServeView(View):
    def get(self, request, job_id, token, filename):
        if not FileSigner().verify(token, str(job_id)):
            raise Http404

        job = DownloadJob.objects.filter(
            pk=job_id, status=JobStatus.SUCCEEDED
        ).first()
        if job is None or not job.relative_path:
            raise Http404

        storage = LocalDiskStorage()
        if not storage.exists(job.relative_path):
            raise Http404

        headers = self._headers(request, job)

        if settings.USE_X_ACCEL:
            response = HttpResponse(b"")
            for key, value in headers.items():
                response[key] = value
            response["X-Accel-Redirect"] = storage.accel_path(job.relative_path)
            return response

        return ranged_file_response(
            request, storage.absolute_path(job.relative_path), headers
        )

    def _headers(self, request, job: DownloadJob) -> dict[str, str]:
        disposition = "attachment" if request.GET.get("dl") else "inline"
        ascii_name, utf8_name = self._filename_headers(job.output_filename)
        return {
            "Content-Type": job.content_type or "application/octet-stream",
            "Content-Disposition": (
                f"{disposition}; filename=\"{ascii_name}\"; filename*=UTF-8''{utf8_name}"
            ),
            "Accept-Ranges": "bytes",
            # Costs nothing, and prevents a class of bug that only appears
            # once the frontend adopts COEP.
            "Cross-Origin-Resource-Policy": "cross-origin",
            "Cache-Control": "private, max-age=600, no-transform",
            "X-Content-Type-Options": "nosniff",
        }

    def _filename_headers(self, name: str) -> tuple[str, str]:
        from urllib.parse import quote

        ascii_name = name.encode("ascii", "ignore").decode() or "download"
        return ascii_name.replace('"', ""), quote(name)
