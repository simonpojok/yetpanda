"""Keeps the media volume from filling up mid-batch."""

import os
import shutil
from enum import StrEnum
from pathlib import Path

from django.conf import settings


class DiskState(StrEnum):
    OK = "ok"
    HIGH = "high"
    CRITICAL = "critical"


class DiskGuard:
    """Two independent brakes: a global watermark and a per-job precheck."""

    def usage_fraction(self) -> float:
        stat = os.statvfs(settings.MEDIA_ROOT)
        total = stat.f_blocks * stat.f_frsize
        if total <= 0:
            return 0.0
        available = stat.f_bavail * stat.f_frsize
        return 1.0 - (available / total)

    def state(self) -> DiskState:
        used = self.usage_fraction()
        if used >= settings.DISK_CRITICAL_WATERMARK:
            return DiskState.CRITICAL
        if used >= settings.DISK_HIGH_WATERMARK:
            return DiskState.HIGH
        return DiskState.OK

    def free_bytes(self, path: Path | None = None) -> int:
        return shutil.disk_usage(path or settings.MEDIA_WORK_ROOT).free

    def has_room_for(self, estimated_bytes: int) -> bool:
        """A merge briefly needs both source streams *and* the output on disk.

        Sizing without the 2x factor is how you end up with a 90%-full volume
        that fails only on large files.
        """
        needed = (estimated_bytes or 0) * 2 + settings.DISK_RESERVE_BYTES
        return self.free_bytes() >= needed
