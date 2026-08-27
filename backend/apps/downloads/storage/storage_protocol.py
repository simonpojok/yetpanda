"""The single seam between the app and the filesystem.

Nothing else in the codebase touches a path. v1 is deliberately one box with
local disk, but every call site goes through this protocol, which is the
difference between a one-day and a two-week migration to object storage.
"""

from pathlib import Path
from typing import BinaryIO, Protocol


class Storage(Protocol):
    def finalize(self, work_dir: Path, job_id: str, filename: str) -> str:
        """Move a finished artifact into place. Returns the relative path."""
        ...

    def absolute_path(self, relative_path: str) -> Path: ...

    def open_stream(self, relative_path: str) -> BinaryIO: ...

    def size_of(self, relative_path: str) -> int: ...

    def delete(self, relative_path: str) -> None: ...

    def accel_path(self, relative_path: str) -> str:
        """Internal path handed to the proxy for X-Accel-style serving."""
        ...
