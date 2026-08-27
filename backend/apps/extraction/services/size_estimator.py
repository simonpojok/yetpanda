"""Estimating file size before anything is downloaded.

YouTube's adaptive formats very often report ``filesize: null``, so a naive
``f["filesize"]`` shows "unknown" on most rows. The cascade below is what
makes the size column actually useful.
"""

# Conservative bits/sec ceilings for video+audio, used before a probe exists.
BITRATE_BY_HEIGHT = {
    2160: 20_000_000,
    1440: 10_000_000,
    1080: 5_000_000,
    720: 2_500_000,
    480: 1_200_000,
    360: 700_000,
    240: 400_000,
    144: 200_000,
}


def estimate_format_size(fmt: dict, duration: float | None) -> tuple[int | None, bool]:
    """Returns ``(bytes, is_estimate)``."""
    if fmt.get("filesize"):
        return int(fmt["filesize"]), False
    if fmt.get("filesize_approx"):
        return int(fmt["filesize_approx"]), True

    tbr = fmt.get("tbr") or ((fmt.get("vbr") or 0) + (fmt.get("abr") or 0)) or None
    if tbr and duration:
        return int(tbr * 1000 / 8 * duration), True  # tbr is kbit/s
    return None, True


def estimate_audio_size(bitrate_kbps: int, duration: float | None) -> int | None:
    if not duration:
        return None
    return int(bitrate_kbps * 1000 / 8 * duration)


def estimate_batch_bytes(durations: list[int | None], kind: str, target: int) -> int:
    """Admission-time sizing for a whole playlist.

    Rejecting a 38GB batch up front with "try 720p (~19GB)" is far better
    than accepting it and failing at item 140.
    """
    if kind == "audio":
        bits_per_second = target * 1000
    else:
        bits_per_second = BITRATE_BY_HEIGHT.get(target, BITRATE_BY_HEIGHT[1080])
    return sum(int((d or 0) * bits_per_second / 8) for d in durations)
