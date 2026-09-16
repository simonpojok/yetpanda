"""MP4 downloads, with optional embedded captions."""

from pathlib import Path

from apps.extraction.options.mp4_options import mp4_options, mp4_with_subtitles_options

from ..models import SubtitleModeChoice
from .base import BaseDownloader

DEFAULT_HEIGHT = 1080


class VideoDownloader(BaseDownloader):
    @property
    def content_type(self) -> str:
        return "video/mp4"

    @property
    def expected_extension(self) -> str:
        return "mp4"

    def build_options(self, spec: dict, work_dir: Path) -> dict:
        height = int(spec.get("height") or DEFAULT_HEIGHT)
        mode = spec.get("subtitle_mode", SubtitleModeChoice.NONE)
        langs = spec.get("subtitle_langs") or []

        if mode == SubtitleModeChoice.EMBED and langs:
            return mp4_with_subtitles_options(
                height, langs, work_dir, logger=self.client.logger
            )
        return mp4_options(height, work_dir, logger=self.client.logger)
