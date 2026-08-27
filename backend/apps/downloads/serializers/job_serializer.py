"""Job representation returned to the client."""

from rest_framework import serializers

from ..models import DownloadJob
from ..services.file_signer import FileSigner


class JobSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()
    error = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()

    class Meta:
        model = DownloadJob
        fields = (
            "id",
            "batch_index",
            "video_id",
            "title",
            "channel",
            "duration",
            "thumbnail_url",
            "kind",
            "status",
            "created_at",
            "progress",
            "error",
            "result",
        )

    def get_progress(self, job: DownloadJob) -> dict:
        live = (self.context.get("progress") or {}).get(str(job.id))
        return live or {
            "stage": job.stage,
            "stage_label": job.get_stage_display(),
            "percent": job.progress_percent,
        }

    def get_error(self, job: DownloadJob) -> dict | None:
        if not job.error_code:
            return None
        from apps.extraction.domain.error_code import RETRYABLE, ErrorCode

        try:
            code = ErrorCode(job.error_code)
        except ValueError:
            code = ErrorCode.UNKNOWN
        return {
            "code": job.error_code,
            "message": job.error_message,
            "retryable": code in RETRYABLE,
        }

    def get_result(self, job: DownloadJob) -> dict | None:
        """URLs are regenerated on every poll, so an open tab never goes stale."""
        if job.status != "succeeded" or not job.relative_path:
            return None
        signer = FileSigner()
        return {
            "filename": job.output_filename,
            "content_type": job.content_type,
            "size_bytes": job.size_bytes,
            "expires_at": job.expires_at,
            "stream_url": signer.build_url(str(job.id), job.output_filename),
            "download_url": signer.build_url(
                str(job.id), job.output_filename, attachment=True
            ),
        }
