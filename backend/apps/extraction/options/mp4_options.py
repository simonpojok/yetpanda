"""Video download options."""

from pathlib import Path

from django.conf import settings

from .base_options import base_options

OUTPUT_TEMPLATE = "%(title).150B [%(id)s].%(ext)s"


def mp4_options(height: int, work_dir: Path, logger=None) -> dict:
    """Prefer H.264 + AAC so the merge is a remux, not a transcode.

    ``merge_output_format: mp4`` will happily hold VP9/Opus, but Safari and
    most TVs then refuse to play it - and the merge stops being a `-c copy`
    that finishes in seconds.
    """
    return base_options(logger) | {
        "paths": {"home": str(work_dir), "temp": str(work_dir)},
        "outtmpl": {"default": OUTPUT_TEMPLATE},
        "format": (
            f"bv*[height<={height}][ext=mp4][vcodec^=avc1]+ba[ext=m4a]/"
            f"bv*[height<={height}][vcodec^=avc1]+ba/"
            f"bv*[height<={height}]+ba/"
            f"b[height<={height}]/"
            f"bv*+ba/b"
        ),
        "format_sort": [f"res:{height}", "vcodec:h264", "acodec:aac", "ext:mp4:m4a", "br"],
        "merge_output_format": "mp4",
        "postprocessors": [
            {"key": "FFmpegVideoRemuxer", "preferedformat": "mp4"},
            {"key": "FFmpegMetadata", "add_metadata": True, "add_chapters": True},
        ],
        # The real guard: probe estimates can be off by 2x, and this aborts
        # mid-download rather than filling the volume.
        "max_filesize": settings.MAX_FILESIZE_BYTES,
    }


def mp4_with_subtitles_options(
    height: int, langs: list[str], work_dir: Path, logger=None
) -> dict:
    """Embed captions into the container.

    ``FFmpegEmbedSubtitle`` must run before the remuxer. MP4 can only carry
    ``mov_text``; MKV is offered separately for full-fidelity SRT.
    """
    options = mp4_options(height, work_dir, logger)
    options |= {
        "writesubtitles": True,
        "writeautomaticsub": False,  # embedding ASR tracks is rarely wanted
        "subtitleslangs": langs,
        "subtitlesformat": "vtt/best",
        "postprocessors": [
            {"key": "FFmpegSubtitlesConvertor", "format": "srt"},
            {"key": "FFmpegEmbedSubtitle", "already_have_subtitle": False},
            {"key": "FFmpegVideoRemuxer", "preferedformat": "mp4"},
            {"key": "FFmpegMetadata", "add_metadata": True, "add_chapters": True},
        ],
    }
    return options
