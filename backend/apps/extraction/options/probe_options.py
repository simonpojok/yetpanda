"""Metadata-only extraction."""

from .base_options import base_options


def video_probe_options(logger=None) -> dict:
    return base_options(logger) | {
        "skip_download": True,
        "extract_flat": False,
        "writesubtitles": False,
        # check_formats would cost one HEAD request per format.
        "check_formats": False,
        # Surface PO-token-gated formats so the UI can disable them rather
        # than letting someone pick a format we know will 403.
        "extractor_args": {"youtube": {"formats": ["missing_pot"]}},
    }


def playlist_probe_options(max_items: int, logger=None) -> dict:
    """Flat extraction: one page walk instead of a player call per video.

    A 200-item playlist expands in seconds this way, versus minutes if each
    entry were fully probed.
    """
    return base_options(logger) | {
        "skip_download": True,
        "noplaylist": False,
        "extract_flat": "in_playlist",
        "lazy_playlist": True,
        "playlistend": max_items,
    }
