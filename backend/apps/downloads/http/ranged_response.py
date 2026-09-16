"""HTTP Range support, because Django has none.

Verified against the installed package: ``grep HTTP_RANGE`` across ``django/``
returns nothing on 4.2 *or* 5.2, and Django ticket #22479 is still open. A
``<video>`` pointed at a bare ``FileResponse`` plays from the start and
refuses to seek - Safari often refuses to play at all, since it opens with
``Range: bytes=0-1``.

In production the proxy serves the bytes; this is the dev path and the
fallback for direct access.
"""

import re
from pathlib import Path
from typing import BinaryIO

from django.http import FileResponse, HttpResponse, HttpResponseBase

# Deliberately only a single simple range. No media element sends multipart
# ranges, and restricting to this form is also what keeps the request
# CORS-safelisted, so media loads never trigger a preflight.
RANGE_PATTERN = re.compile(r"^bytes=(\d*)-(\d*)$")

CHUNK_SIZE = 64 * 1024


class _LimitedReader:
    """Yields at most ``length`` bytes from an open file handle."""

    def __init__(self, handle: BinaryIO, length: int) -> None:
        self._handle = handle
        self._remaining = length

    def __iter__(self):
        return self

    def __next__(self) -> bytes:
        if self._remaining <= 0:
            self._handle.close()
            raise StopIteration
        chunk = self._handle.read(min(CHUNK_SIZE, self._remaining))
        if not chunk:
            self._handle.close()
            raise StopIteration
        self._remaining -= len(chunk)
        return chunk

    def close(self) -> None:
        self._handle.close()


def ranged_file_response(
    request, path: Path, headers: dict[str, str]
) -> HttpResponseBase:
    size = path.stat().st_size
    raw_range = request.META.get("HTTP_RANGE", "")
    match = RANGE_PATTERN.match(raw_range.strip()) if raw_range else None

    if not match:
        response = FileResponse(path.open("rb"))
        response["Content-Length"] = str(size)
    else:
        bounds = _resolve_bounds(match, size)
        if bounds is None:
            return _range_not_satisfiable(size, headers)
        start, end = bounds
        length = end - start + 1

        handle = path.open("rb")
        handle.seek(start)
        response = FileResponse(_LimitedReader(handle, length), status=206)
        response["Content-Length"] = str(length)
        response["Content-Range"] = f"bytes {start}-{end}/{size}"

    for key, value in headers.items():
        response[key] = value
    return response


def _resolve_bounds(match: re.Match, size: int) -> tuple[int, int] | None:
    start_raw, end_raw = match.groups()
    if not start_raw and not end_raw:
        return None

    if not start_raw:  # suffix range, e.g. bytes=-500
        length = min(int(end_raw), size)
        if length <= 0:
            return None
        return size - length, size - 1

    start = int(start_raw)
    end = min(int(end_raw), size - 1) if end_raw else size - 1
    if start > end or start >= size:
        return None
    return start, end


def _range_not_satisfiable(size: int, headers: dict[str, str]) -> HttpResponse:
    response = HttpResponse(status=416)
    response["Content-Range"] = f"bytes */{size}"
    for key, value in headers.items():
        response[key] = value
    return response
