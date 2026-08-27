"""Audio download options."""

from pathlib import Path

from django.conf import settings

from .base_options import base_options
from .mp4_options import OUTPUT_TEMPLATE

MP3_BITRATES = (128, 192, 256, 320)
DEFAULT_BITRATE = 192


def mp3_options(bitrate_kbps: int, work_dir: Path, logger=None) -> dict:
    """Extract to MP3 at a target bitrate.

    ``EmbedThumbnail`` must come after ``FFmpegExtractAudio`` - yt-dlp runs
    postprocessors in list order and the artwork goes into the finished MP3.
    """
    return base_options(logger) | {
        "paths": {"home": str(work_dir), "temp": str(work_dir)},
        "outtmpl": {"default": OUTPUT_TEMPLATE},
        "format": "ba[acodec^=opus]/ba[ext=m4a]/ba/b",
        "format_sort": ["abr", "asr"],
        "writethumbnail": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": str(bitrate_kbps),
                "nopostoverwrites": False,
            },
            {"key": "FFmpegMetadata", "add_metadata": True},
            {"key": "EmbedThumbnail", "already_have_thumbnail": False},
        ],
        "max_filesize": settings.MAX_FILESIZE_BYTES,
    }


def passthrough_audio_options(work_dir: Path, logger=None) -> dict:
    """Original audio, no re-encode.

    YouTube's best audio is ~128kbps Opus, so a 320kbps MP3 is strictly
    larger with no added fidelity. This option exists for people who want the
    source untouched.
    """
    return base_options(logger) | {
        "paths": {"home": str(work_dir), "temp": str(work_dir)},
        "outtmpl": {"default": OUTPUT_TEMPLATE},
        "format": "ba[ext=m4a]/ba/b",
        "postprocessors": [{"key": "FFmpegMetadata", "add_metadata": True}],
        "max_filesize": settings.MAX_FILESIZE_BYTES,
    }
