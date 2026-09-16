"""Status and stage vocabularies.

Stored as varchar + CHECK rather than native Postgres enums: ``ALTER TYPE
... ADD VALUE`` cannot run inside a transaction, which makes adding a status
later a zero-downtime headache for a few saved bytes.
"""

from django.db import models


class JobStatus(models.TextChoices):
    QUEUED = "queued", "Queued"
    DISPATCHED = "dispatched", "Dispatched"
    RUNNING = "running", "Running"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"
    SKIPPED = "skipped", "Skipped"
    EXPIRED = "expired", "Expired"


ACTIVE_JOB_STATUSES = (JobStatus.DISPATCHED, JobStatus.RUNNING)
TERMINAL_JOB_STATUSES = (
    JobStatus.SUCCEEDED,
    JobStatus.FAILED,
    JobStatus.CANCELLED,
    JobStatus.SKIPPED,
    JobStatus.EXPIRED,
)


class JobStage(models.TextChoices):
    PENDING = "pending", "Pending"
    RESOLVING = "resolving", "Resolving"
    DOWNLOADING_VIDEO = "downloading_video", "Downloading video"
    DOWNLOADING_AUDIO = "downloading_audio", "Downloading audio"
    DOWNLOADING_SUBS = "downloading_subs", "Downloading subtitles"
    MERGING = "merging", "Merging"
    TRANSCODING = "transcoding", "Converting"
    REMUXING = "remuxing", "Remuxing"
    EMBEDDING_SUBS = "embedding_subs", "Embedding subtitles"
    EMBEDDING_META = "embedding_meta", "Adding metadata"
    FINALIZING = "finalizing", "Finalizing"
    DONE = "done", "Done"
    FAILED = "failed", "Failed"


class BatchStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    RUNNING = "running", "Running"
    COMPLETED = "completed", "Completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors", "Completed with errors"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


TERMINAL_BATCH_STATUSES = (
    BatchStatus.COMPLETED,
    BatchStatus.COMPLETED_WITH_ERRORS,
    BatchStatus.FAILED,
    BatchStatus.CANCELLED,
)


class MediaKindChoice(models.TextChoices):
    VIDEO = "video", "Video"
    AUDIO = "audio", "Audio"


class SubtitleModeChoice(models.TextChoices):
    NONE = "none", "None"
    SEPARATE = "separate", "Separate file"
    EMBED = "embed", "Embedded"


class SourceKindChoice(models.TextChoices):
    VIDEO = "video", "Video"
    PLAYLIST = "playlist", "Playlist"
