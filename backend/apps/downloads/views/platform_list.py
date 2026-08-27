"""GET /v1/platforms"""

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.extraction.registry.platform_registry import PlatformRegistry


class PlatformListView(APIView):
    """Lists every platform, flagging which are downloadable today."""

    def get(self, request):
        registry = PlatformRegistry()
        return Response({"platforms": [p.as_dict() for p in registry.all()]})
