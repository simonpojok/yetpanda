"""The canonicaliser is the SSRF boundary, so it gets the hardest tests."""

import pytest

from apps.extraction.domain.error_code import ErrorCode
from apps.extraction.domain.exceptions import UnsupportedUrlError
from apps.extraction.domain.media_kind import SourceKind
from apps.extraction.services.url_canonicalizer import UrlCanonicalizer

CANON = UrlCanonicalizer()

VIDEO_CASES = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "http://youtube.com/watch?v=dQw4w9WgXcQ",
    "https://m.youtube.com/watch?v=dQw4w9WgXcQ&t=42s",
    "https://music.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ?t=10",
    "https://www.youtube.com/shorts/dQw4w9WgXcQ",
    "https://www.youtube.com/embed/dQw4w9WgXcQ",
    "https://www.youtube.com/live/dQw4w9WgXcQ",
    "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
    "  https://www.youtube.com/watch?v=dQw4w9WgXcQ  ",
    "www.youtube.com/watch?v=dQw4w9WgXcQ",
]


@pytest.mark.parametrize("raw", VIDEO_CASES)
def test_video_urls_normalise_to_one_canonical_form(raw):
    result = CANON.canonicalize(raw)
    assert result.source_kind is SourceKind.VIDEO
    assert result.external_id == "dQw4w9WgXcQ"
    assert result.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_playlist_url():
    result = CANON.canonicalize(
        "https://www.youtube.com/playlist?list=PLFgquLnL59alCl_2TQvOiD5Vgm1hCaGSI"
    )
    assert result.source_kind is SourceKind.PLAYLIST
    assert result.url == (
        "https://www.youtube.com/playlist?list=PLFgquLnL59alCl_2TQvOiD5Vgm1hCaGSI"
    )


def test_watch_url_carrying_a_list_is_treated_as_a_playlist():
    result = CANON.canonicalize(
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLFgquLnL59alCl_2TQvOiD5Vgm1hCaGSI"
    )
    assert result.source_kind is SourceKind.PLAYLIST


@pytest.mark.parametrize("prefix", ["RD", "UL", "LL", "MM"])
def test_auto_generated_mixes_fall_back_to_the_video(prefix):
    """Mixes are unbounded, so we take the video rather than expanding."""
    raw = f"https://www.youtube.com/watch?v=dQw4w9WgXcQ&list={prefix}MMabcdefghijkl"
    result = CANON.canonicalize(raw)
    assert result.source_kind is SourceKind.VIDEO


# --- the part that actually matters -----------------------------------------

SSRF_CASES = [
    "http://169.254.169.254/latest/meta-data/",
    "http://localhost:6379/",
    "http://127.0.0.1:8000/admin/",
    "http://10.0.0.1/",
    "http://192.168.1.1/",
    "http://[::1]:6379/",
    "file:///etc/passwd",
    "gopher://127.0.0.1:6379/_FLUSHALL",
    "http://metadata.google.internal/computeMetadata/v1/",
    "https://evil.com/watch?v=dQw4w9WgXcQ",
    "https://youtube.com.evil.com/watch?v=dQw4w9WgXcQ",
    "https://notyoutube.com/watch?v=dQw4w9WgXcQ",
]


@pytest.mark.parametrize("raw", SSRF_CASES)
def test_non_youtube_hosts_are_rejected(raw):
    with pytest.raises(UnsupportedUrlError) as exc:
        CANON.canonicalize(raw)
    assert exc.value.code in (ErrorCode.UNSUPPORTED_HOST, ErrorCode.INVALID_URL)


MALFORMED_CASES = [
    "",
    "   ",
    "https://www.youtube.com/",
    "https://www.youtube.com/watch",
    "https://www.youtube.com/watch?v=tooshort",
    "https://www.youtube.com/watch?v=" + "x" * 64,
    "https://www.youtube.com/watch?v=has spaces!",
    "https://www.youtube.com/watch?v=" + "a" * 3000,
]


@pytest.mark.parametrize("raw", MALFORMED_CASES)
def test_malformed_input_is_rejected(raw):
    with pytest.raises(UnsupportedUrlError):
        CANON.canonicalize(raw)


def test_rebuilt_url_never_carries_user_query_params():
    """Whatever the user appended must not survive into what yt-dlp sees."""
    result = CANON.canonicalize(
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&evil=1&proxy=http://127.0.0.1"
    )
    assert result.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert "evil" not in result.url and "127.0.0.1" not in result.url
