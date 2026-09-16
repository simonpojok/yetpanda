"""The one platform that actually works today."""

from ..domain.platform import Platform

YOUTUBE = Platform(
    id="youtube",
    name="YouTube",
    available=True,
    hostnames=(
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
        "youtu.be",
        "youtube-nocookie.com",
    ),
)
