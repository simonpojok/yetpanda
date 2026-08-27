"""A caption file emitted alongside a job in 'separate' subtitle mode."""

import uuid

from django.db import models


class SubtitleAsset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(
        "downloads.DownloadJob", on_delete=models.CASCADE, related_name="subtitles"
    )
    lang = models.CharField(max_length=16)
    lang_name = models.CharField(max_length=64, blank=True)
    is_auto = models.BooleanField(default=False)
    fmt = models.CharField(max_length=8)
    relative_path = models.TextField()
    size_bytes = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["job", "lang", "fmt", "is_auto"], name="uq_sub_per_job"
            )
        ]

    def __str__(self) -> str:
        return f"{self.lang}.{self.fmt}"
