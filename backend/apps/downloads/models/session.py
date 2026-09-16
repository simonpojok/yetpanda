"""Anonymous, cookie-backed identity. Deliberately holds no PII."""

import hashlib
import uuid

from django.conf import settings
from django.db import models


class Session(models.Model):
    """One browser, identified by a signed cookie we minted.

    ``ip_hash`` is the abuse backstop: the cookie is clearable, so every quota
    is also evaluated against the (salted, truncated) IP. The raw address is
    never stored.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip_hash = models.CharField(max_length=32, db_index=True)
    user_agent_hash = models.CharField(max_length=32, blank=True)
    bytes_used = models.BigIntegerField(default=0)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["last_seen_at"], name="ix_session_last_seen")]

    def __str__(self) -> str:
        return f"Session {self.id}"

    @staticmethod
    def hash_ip(ip: str) -> str:
        salted = f"{ip}{settings.IP_HASH_SALT}".encode()
        return hashlib.sha256(salted).hexdigest()[:32]
