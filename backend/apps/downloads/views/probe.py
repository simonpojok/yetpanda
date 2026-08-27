"""POST /v1/probe - read a URL and describe what can be downloaded."""

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.extraction.domain.media_kind import SourceKind
from apps.extraction.services.playlist_expander import PlaylistExpander
from apps.extraction.services.probe_service import ProbeService
from apps.extraction.services.url_canonicalizer import UrlCanonicalizer

from ..models import ProbeCache
from ..serializers.probe_request_serializer import ProbeRequestSerializer


class ProbeView(APIView):
    def post(self, request):
        payload = ProbeRequestSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        # Canonicalise first: everything downstream sees a URL we built.
        canonical = UrlCanonicalizer().canonicalize(payload.validated_data["url"])

        cached = self._cached(canonical)
        if cached is not None:
            return Response(cached)

        if canonical.source_kind is SourceKind.PLAYLIST:
            result = PlaylistExpander().expand(canonical).as_dict()
        else:
            result = ProbeService().probe_video(canonical).as_dict()

        result["source_url"] = canonical.url
        self._store(canonical, result)
        return Response(result)

    def _cached(self, canonical) -> dict | None:
        row = ProbeCache.objects.filter(
            source="youtube",
            content_type=canonical.source_kind,
            external_id=canonical.external_id,
            expires_at__gt=timezone.now(),
        ).first()
        return row.payload if row else None

    def _store(self, canonical, result: dict) -> None:
        ProbeCache.objects.update_or_create(
            source="youtube",
            content_type=canonical.source_kind,
            external_id=canonical.external_id,
            defaults={
                "title": result.get("title", ""),
                "channel": result.get("channel", ""),
                "duration": result.get("duration"),
                "item_count": result.get("item_count"),
                "thumbnail_url": result.get("thumbnail_url", ""),
                "is_live": result.get("is_live", False),
                "payload": result,
                "expires_at": ProbeService.expires_at(),
            },
        )
