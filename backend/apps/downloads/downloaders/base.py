"""Common shape for every downloader."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DownloadResult:
    filename: str
    content_type: str
    size_bytes: int
    subtitle_files: tuple[str, ...] = ()


class BaseDownloader(ABC):
    """Builds options, runs the extraction, reports what landed on disk."""

    def __init__(self, client, hooks: dict) -> None:
        self.client = client
        self.hooks = hooks

    @abstractmethod
    def build_options(self, spec: dict, work_dir: Path) -> dict: ...

    @property
    @abstractmethod
    def content_type(self) -> str: ...

    @property
    @abstractmethod
    def expected_extension(self) -> str: ...

    def download(self, url: str, spec: dict, work_dir: Path) -> DownloadResult:
        options = self.build_options(spec, work_dir) | self.hooks
        self.client.extract(url, options, download=True)
        return self._collect(work_dir)

    def _collect(self, work_dir: Path) -> DownloadResult:
        """Find the finished artifact.

        yt-dlp's final filename depends on postprocessors, so we look for what
        actually exists rather than predicting the name.
        """
        media = [
            p
            for p in work_dir.iterdir()
            if p.is_file() and p.suffix.lower() == f".{self.expected_extension}"
        ]
        if not media:
            raise FileNotFoundError(
                f"no .{self.expected_extension} produced in {work_dir}"
            )
        output = max(media, key=lambda p: p.stat().st_size)
        subtitles = tuple(
            p.name for p in work_dir.iterdir() if p.suffix.lower() in (".srt", ".vtt")
        )
        return DownloadResult(
            filename=output.name,
            content_type=self.content_type,
            size_bytes=output.stat().st_size,
            subtitle_files=subtitles,
        )
