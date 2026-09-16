"""Standalone caption downloads."""

from pathlib import Path

from .base_options import base_options
from .mp4_options import OUTPUT_TEMPLATE

SUBTITLE_FORMATS = ("srt", "vtt")


def subtitle_only_options(
    langs: list[str], fmt: str, work_dir: Path, logger=None
) -> dict:
    """YouTube serves vtt/srv3/ttml and never SRT.

    Asking for ``subtitlesformat: "srt"`` alone silently yields whatever is
    "best", so the converter postprocessor is mandatory for a real .srt.
    """
    options = base_options(logger) | {
        "paths": {"home": str(work_dir), "temp": str(work_dir)},
        "outtmpl": {"default": OUTPUT_TEMPLATE},
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": langs,
        "subtitlesformat": "vtt/srv3/best",
    }
    if fmt == "srt":
        options["postprocessors"] = [
            {"key": "FFmpegSubtitlesConvertor", "format": "srt"}
        ]
    return options
