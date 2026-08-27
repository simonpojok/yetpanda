"""POST /v1/jobs - queue a single download."""

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.extraction.domain.error_code import ErrorCode
from apps.extraction.domain.exceptions import PolicyError
from apps.extraction.domain.media_kind import MediaKind, SourceKind
from apps.extraction.services.probe_service import ProbeService
from apps.extraction.services.url_canonicalizer import UrlCanonicalizer

from ..serializers.job_create_serializer import JobCreateSerializer
from ..serializers.job_serializer import JobSerializer
from ..services.job_creation import JobCreationService
from ..services.session_resolver import SessionResolver


class JobCreateView(APIView):
    def post(self, request):
        payload = JobCreateSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        canonical = UrlCanonicalizer().canonicalize(payload.validated_data["url"])
        if canonical.source_kind is SourceKind.PLAYLIST:
            raise PolicyError(
                ErrorCode.INVALID_URL, "use /v1/batches for a playlist"
            )

        probe = ProbeService().probe_video(canonical)
        spec = payload.to_spec()

        job = JobCreationService().create(
            session=SessionResolver().resolve(request),
            ip_hash=request.client_ip_hash,
            probe=probe,
            source_url=canonical.url,
            kind=payload.validated_data["kind"],
            spec=spec,
            est_bytes=self._estimate(probe, payload.validated_data),
        )
        return Response(JobSerializer(job).data, status=201)

    def _estimate(self, probe, data: dict) -> int | None:
        if data["kind"] == MediaKind.AUDIO:
            option_id = "audio:original" if data.get("passthrough") else None
            bitrate = data.get("audio_bitrate_kbps")
            for option in probe.formats.audio:
                if option_id and option.is_passthrough:
                    return option.size_bytes
                if bitrate and option.bitrate_kbps == bitrate:
                    return option.size_bytes
            return None

        height = data.get("height")
        for option in probe.formats.video:
            if option.height == height:
                return option.size_bytes
        return None
