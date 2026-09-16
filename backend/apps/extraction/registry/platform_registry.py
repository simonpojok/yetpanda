"""Which platforms exist, and which of them we can actually serve.

The unavailable entries are deliberately UI-only. Their extractors are never
added to yt-dlp's ``allowed_extractors`` - that is how an allowlist quietly
stops being an allowlist.
"""

from ..domain.platform import Platform
from .youtube_platform import YOUTUBE

_COMING_SOON = (
    Platform(id="tiktok", name="TikTok", available=False),
    Platform(id="x", name="X", available=False),
    Platform(id="facebook", name="Facebook", available=False),
    Platform(id="instagram", name="Instagram", available=False),
)


class PlatformRegistry:
    def all(self) -> list[Platform]:
        return [YOUTUBE, *_COMING_SOON]

    def available(self) -> list[Platform]:
        return [p for p in self.all() if p.available]
