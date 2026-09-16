"""Translate yt-dlp's hook payloads into our stage vocabulary.

yt-dlp never says "this is the video stream" - you infer it from the codecs on
the format currently being downloaded.
"""

from apps.downloads.models import JobStage

STAGE_BY_POSTPROCESSOR = {
    "Merger": JobStage.MERGING,
    "FFmpegVideoRemuxer": JobStage.REMUXING,
    "FFmpegVideoConvertor": JobStage.TRANSCODING,
    "FFmpegExtractAudio": JobStage.TRANSCODING,
    "FFmpegEmbedSubtitle": JobStage.EMBEDDING_SUBS,
    "FFmpegSubtitlesConvertor": JobStage.DOWNLOADING_SUBS,
    "EmbedThumbnail": JobStage.EMBEDDING_META,
    "FFmpegMetadata": JobStage.EMBEDDING_META,
    "MoveFiles": JobStage.FINALIZING,
}


def stage_for_download(info: dict) -> JobStage:
    """Audio-only formats report ``vcodec: 'none'``."""
    vcodec = (info or {}).get("vcodec")
    if vcodec in (None, "none"):
        return JobStage.DOWNLOADING_AUDIO
    return JobStage.DOWNLOADING_VIDEO


def stage_for_postprocessor(name: str) -> JobStage:
    return STAGE_BY_POSTPROCESSOR.get(name, JobStage.FINALIZING)


def total_bytes_from(status: dict) -> int | None:
    """``total_bytes`` is frequently absent; fall back the way yt-dlp does."""
    return status.get("total_bytes") or status.get("total_bytes_estimate")
