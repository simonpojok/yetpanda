"""GET /v1/batches/{id}/archive.zip - stream a batch as one archive.

zipstream-ng generates the archive lazily, so a 50-track download never
materialises on disk. ZIP_STORED is deliberate: MP4/MP3 are already
compressed, so deflate burns CPU for nothing - and STORED lets us compute an
exact Content-Length up front, which gives the browser a real progress bar
instead of an indeterminate chunked transfer.

Range/resume is explicitly unsupported: a generated ZIP has no random access,
so honouring a seek would mean re-reading everything before it. Per-file
downloads remain the resumable path.
"""

import logging

from django.conf import settings
from django.http import Http404, JsonResponse, StreamingHttpResponse
from django.views import View
from zipstream import ZIP_STORED, ZipStream

from ..models import BatchStatus, DownloadBatch, JobStatus
from ..storage.local_disk_storage import LocalDiskStorage

logger = logging.getLogger(__name__)


class BatchArchiveView(View):
    def get(self, request, batch_id):
        batch = DownloadBatch.objects.filter(
            pk=batch_id, session_id=request.anon_session_id
        ).first()
        if batch is None:
            raise Http404

        if not batch.is_terminal:
            return JsonResponse(
                {"error": {"code": "batch_not_finished", "message": "Still downloading."}},
                status=409,
            )

        items = list(
            batch.items.filter(status=JobStatus.SUCCEEDED).order_by("batch_index")
        )
        if not items:
            return JsonResponse(
                {"error": {"code": "nothing_to_download", "message": "Nothing finished."}},
                status=404,
            )

        storage = LocalDiskStorage()
        stream = ZipStream(compress_type=ZIP_STORED, sized=True)
        for position, job in enumerate(items, start=1):
            if not storage.exists(job.relative_path):
                continue
            stream.add_path(
                storage.absolute_path(job.relative_path),
                arcname=f"{position:03d} - {job.output_filename}",
            )

        filename = self._archive_name(batch)
        response = StreamingHttpResponse(stream, content_type="application/zip")
        response["Content-Length"] = str(len(stream))
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response["Accept-Ranges"] = "none"
        # Without this the proxy would buffer the whole archive to a temp
        # file, reintroducing exactly the disk write we are avoiding.
        response["X-Accel-Buffering"] = "no"
        response["Cache-Control"] = "no-store"
        return response

    def _archive_name(self, batch: DownloadBatch) -> str:
        base = "".join(
            c for c in (batch.title or "yetpanda") if c.isalnum() or c in " -_"
        ).strip()
        return f"{base or 'yetpanda'}.zip"
