"""Local-disk implementation of :class:`Storage`."""

import shutil
from pathlib import Path
from typing import BinaryIO
from urllib.parse import quote

from django.conf import settings


class LocalDiskStorage:
    """Work and done roots must share a filesystem so finalize is atomic."""

    @property
    def work_root(self) -> Path:
        return Path(settings.MEDIA_WORK_ROOT)

    @property
    def done_root(self) -> Path:
        return Path(settings.MEDIA_DONE_ROOT)

    def work_dir(self, job_id: str) -> Path:
        path = self.work_root / str(job_id)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def finalize(self, work_dir: Path, job_id: str, filename: str) -> str:
        """``os.replace`` within one filesystem is atomic and instant.

        The row is only flipped to succeeded after this returns, so a reader
        can never observe a half-written file.
        """
        destination_dir = self.done_root / str(job_id)
        destination_dir.mkdir(parents=True, exist_ok=True)
        source = work_dir / filename
        destination = destination_dir / filename
        source.replace(destination)
        return f"{job_id}/{filename}"

    def absolute_path(self, relative_path: str) -> Path:
        resolved = (self.done_root / relative_path).resolve()
        root = self.done_root.resolve()
        if not resolved.is_relative_to(root):
            raise ValueError("path escapes the media root")
        return resolved

    def open_stream(self, relative_path: str) -> BinaryIO:
        return self.absolute_path(relative_path).open("rb")

    def size_of(self, relative_path: str) -> int:
        return self.absolute_path(relative_path).stat().st_size

    def exists(self, relative_path: str) -> bool:
        try:
            return self.absolute_path(relative_path).is_file()
        except (ValueError, OSError):
            return False

    def delete(self, relative_path: str) -> None:
        try:
            self.absolute_path(relative_path).unlink(missing_ok=True)
        except (ValueError, OSError):
            pass

    def delete_job_dir(self, job_id: str) -> None:
        shutil.rmtree(self.done_root / str(job_id), ignore_errors=True)

    def accel_path(self, relative_path: str) -> str:
        return settings.X_ACCEL_PREFIX + quote(relative_path)
