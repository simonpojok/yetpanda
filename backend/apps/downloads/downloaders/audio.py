"""MP3 downloads, plus the no-re-encode passthrough."""

from pathlib import Path

from apps.extraction.options.mp3_options import (
    DEFAULT_BITRATE,
    mp3_options,
    passthrough_audio_options,
)

from .base import BaseDownloader


class AudioDownloader(BaseDownloader):
    def __init__(self, client, hooks: dict, passthrough: bool = False) -> None:
        super().__init__(client, hooks)
        self.passthrough = passthrough

    @property
    def content_type(self) -> str:
        return "audio/mp4" if self.passthrough else "audio/mpeg"

    @property
    def expected_extension(self) -> str:
        return "m4a" if self.passthrough else "mp3"

    def build_options(self, spec: dict, work_dir: Path) -> dict:
        if self.passthrough:
            return passthrough_audio_options(work_dir, logger=self.client.logger)
        bitrate = int(spec.get("audio_bitrate_kbps") or DEFAULT_BITRATE)
        return mp3_options(bitrate, work_dir, logger=self.client.logger)
