"""Create a bulk playlist download: one preference, many children."""

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.extraction.domain.error_code import ErrorCode
from apps.extraction.domain.exceptions import PolicyError
from apps.extraction.domain.media_kind import MediaKind
from apps.extraction.domain.probe_result import PlaylistProbe
from apps.extraction.services.size_estimator import estimate_batch_bytes

from ..models import BatchStatus, DownloadBatch, DownloadJob, JobStatus, Session

BATCH_ITEM_PRIORITY = 0


class BatchCreationService:
    def create(
        self,
        *,
        session: Session,
        ip_hash: str,
        probe: PlaylistProbe,
        source_url: str,
        kind: str,
        spec: dict,
        selected_indexes: list[int] | None,
    ) -> DownloadBatch:
        selected = self._select(probe, selected_indexes)
        est_bytes = self._estimate(selected, kind, spec)
        self._enforce_policy(session, selected, est_bytes, kind)

        now = timezone.now()
        with transaction.atomic():
            batch = DownloadBatch.objects.create(
                session=session,
                client_ip_hash=ip_hash,
                source_url=source_url,
                playlist_id=probe.playlist_id,
                title=probe.title,
                kind=kind,
                preference=spec,
                total_items=len(selected),
                est_total_bytes=est_bytes,
                status=BatchStatus.PENDING,
                expires_at=now
                + timezone.timedelta(seconds=settings.BATCH_TTL_SECONDS),
            )

            DownloadJob.objects.bulk_create(
                [
                    DownloadJob(
                        session=session,
                        batch=batch,
                        batch_index=position,
                        client_ip_hash=ip_hash,
                        source_url=f"https://www.youtube.com/watch?v={entry.video_id}",
                        video_id=entry.video_id,
                        title=entry.title,
                        duration=entry.duration,
                        thumbnail_url=entry.thumbnail_url,
                        kind=kind,
                        spec=spec,
                        subtitle_mode=spec.get("subtitle_mode", "none"),
                        subtitle_langs=spec.get("subtitle_langs") or [],
                        priority=BATCH_ITEM_PRIORITY,
                        status=JobStatus.QUEUED,
                        expires_at=batch.expires_at,
                    )
                    for position, entry in enumerate(selected)
                ]
            )
        return batch

    def _select(self, probe: PlaylistProbe, indexes: list[int] | None):
        """Unavailable and over-long items are skipped, not failed.

        They are also excluded from ``total_items`` so a batch showing
        "17 of 48" always actually reaches 48.
        """
        wanted = set(indexes) if indexes else None
        selected = []
        for entry in probe.entries:
            if wanted is not None and entry.index not in wanted:
                continue
            if not entry.is_available:
                continue
            if (
                entry.duration
                and entry.duration > settings.MAX_BATCH_ITEM_DURATION_SECONDS
            ):
                continue
            selected.append(entry)
        return selected

    def _estimate(self, selected, kind: str, spec: dict) -> int:
        target = (
            spec.get("audio_bitrate_kbps", 192)
            if kind == MediaKind.AUDIO
            else spec.get("height", 1080)
        )
        return estimate_batch_bytes([e.duration for e in selected], kind, target)

    def _enforce_policy(self, session, selected, est_bytes: int, kind: str) -> None:
        if not selected:
            raise PolicyError(ErrorCode.NOT_FOUND, "no downloadable items selected")
        if len(selected) > settings.MAX_BATCH_ITEMS:
            raise PolicyError(ErrorCode.TOO_LARGE, f"{len(selected)} items")

        cap = (
            settings.MAX_BATCH_BYTES_AUDIO
            if kind == MediaKind.AUDIO
            else settings.MAX_BATCH_BYTES_VIDEO
        )
        if est_bytes > cap:
            # Reject up front with a number rather than failing at item 140.
            raise PolicyError(
                ErrorCode.TOO_LARGE,
                f"estimated {est_bytes // 1024**3}GB exceeds the {cap // 1024**3}GB limit",
            )
        if session.bytes_used >= settings.MAX_SESSION_BYTES_PER_DAY:
            raise PolicyError(ErrorCode.QUOTA_EXCEEDED, "daily byte quota")
