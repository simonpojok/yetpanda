"""Turn domain errors into the one error envelope the frontend understands."""

import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from apps.extraction.domain.error_code import ErrorCode
from apps.extraction.domain.exceptions import YetPandaError

logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    if isinstance(exc, YetPandaError):
        # ``detail`` can carry yt-dlp internals, so it is logged, never returned.
        logger.warning("api error %s: %s", exc.code, exc.detail)
        return Response(
            {
                "error": {
                    "code": str(exc.code),
                    "message": exc.message,
                    "retryable": exc.retryable,
                }
            },
            status=exc.http_status,
        )

    response = drf_exception_handler(exc, context)
    if response is not None:
        return response

    logger.exception("unhandled api error")
    return Response(
        {
            "error": {
                "code": str(ErrorCode.UNKNOWN),
                "message": "Something went wrong. Try again.",
                "retryable": False,
            }
        },
        status=500,
    )
