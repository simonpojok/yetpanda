"""Create a single download job."""

from django.conf import settings
from django.utils import timezone

from apps.extraction.domain.error_code import ErrorCode
from apps.extraction.domain.exceptions import PolicyError
from apps.extraction.domain.media_kind import MediaKind
from apps.extraction.domain.probe_result import VideoProbe

from ..models import DownloadJob, JobStatus, Session

SINGLE_JOB_PRIORITY = 10


class JobCreationService:
    def create(
        self,
        *,
        session: Session,
        ip_hash: str,
        probe: VideoProbe,
        source_url: str,
        kind: str,
        spec: dict,
        est_bytes: int | None,
    ) -> DownloadJob:
        self._enforce_policy(session, probe, est_bytes)

        return DownloadJob.objects.create(
            session=session,
            client_ip_hash=ip_hash,
            source_url=source_url,
            video_id=probe.video_id,
            title=probe.title,
            channel=probe.channel,
            duration=probe.duration,
            thumbnail_url=probe.thumbnail_url,
            kind=kind,
            spec=spec,
            subtitle_mode=spec.get("subtitle_mode", "none"),
            subtitle_langs=spec.get("subtitle_langs") or [],
            est_total_bytes=est_bytes,
            priority=SINGLE_JOB_PRIORITY,
            status=JobStatus.QUEUED,
            expires_at=timezone.now()
            + timezone.timedelta(seconds=settings.JOB_TTL_SECONDS),
        )

    def _enforce_policy(self, session, probe: VideoProbe, est_bytes: int | None) -> None:
        if probe.is_live:
            raise PolicyError(ErrorCode.LIVE_NOT_SUPPORTED, probe.video_id)
        if probe.duration and probe.duration > settings.MAX_DURATION_SECONDS:
            raise PolicyError(ErrorCode.TOO_LONG, f"{probe.duration}s")
        if est_bytes and est_bytes > settings.MAX_FILESIZE_BYTES:
            raise PolicyError(ErrorCode.TOO_LARGE, f"{est_bytes} bytes")
        if session.bytes_used >= settings.MAX_SESSION_BYTES_PER_DAY:
            raise PolicyError(ErrorCode.QUOTA_EXCEEDED, "daily byte quota")
