"""POST /v1/batches - queue a whole playlist with one preference."""

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.extraction.domain.error_code import ErrorCode
from apps.extraction.domain.exceptions import PolicyError
from apps.extraction.domain.media_kind import SourceKind
from apps.extraction.services.playlist_expander import PlaylistExpander
from apps.extraction.services.url_canonicalizer import UrlCanonicalizer

from ..serializers.batch_create_serializer import BatchCreateSerializer
from ..serializers.batch_serializer import BatchSerializer
from ..services.batch_creation import BatchCreationService
from ..services.session_resolver import SessionResolver


class BatchCreateView(APIView):
    def post(self, request):
        payload = BatchCreateSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        canonical = UrlCanonicalizer().canonicalize(payload.validated_data["url"])
        if canonical.source_kind is not SourceKind.PLAYLIST:
            raise PolicyError(ErrorCode.INVALID_URL, "not a playlist link")

        probe = PlaylistExpander().expand(canonical)
        batch = BatchCreationService().create(
            session=SessionResolver().resolve(request),
            ip_hash=request.client_ip_hash,
            probe=probe,
            source_url=canonical.url,
            kind=payload.validated_data["kind"],
            spec=payload.to_spec(),
            selected_indexes=payload.validated_data.get("item_indexes"),
        )
        return Response(BatchSerializer(batch).data, status=201)
