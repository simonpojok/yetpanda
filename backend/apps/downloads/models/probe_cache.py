"""Cached extraction results.

Metadata is stable for days, but ``formats[].url`` values are signed,
IP-bound and expire in roughly six hours. We therefore strip those URLs
before storing and always re-resolve at download time from the stable format
*selector string*. Persisting them would produce an intermittent 403 that
only reproduces after six hours.
"""

import uuid

from django.db import models

from .enums import SourceKindChoice


class ProbeCache(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.CharField(max_length=16, default="youtube")
    content_type = models.CharField(max_length=16, choices=SourceKindChoice.choices)
    external_id = models.CharField(max_length=64)

    title = models.TextField()
    channel = models.TextField(blank=True)
    duration = models.IntegerField(null=True, blank=True)
    item_count = models.IntegerField(null=True, blank=True)
    thumbnail_url = models.TextField(blank=True)
    is_live = models.BooleanField(default=False)

    payload = models.JSONField(help_text="Normalised, UI-facing probe result.")

    fetched_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "content_type", "external_id"],
                name="uq_probe_identity",
            )
        ]
        indexes = [models.Index(fields=["expires_at"], name="ix_probe_expiry")]

    def __str__(self) -> str:
        return f"{self.content_type}:{self.external_id}"
