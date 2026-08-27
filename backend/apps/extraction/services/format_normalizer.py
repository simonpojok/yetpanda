"""Turn yt-dlp's raw ``formats`` array into a list a person can choose from.

Two decisions drive this: video is presented **by height**, because nobody
wants to pick a format id; and audio is presented **by target bitrate**,
because the source is transcoded regardless, so offering "251kbps Opus webm"
tells the user nothing.
"""

from ..domain.media_format import AudioOption, FormatCatalogue, VideoOption
from ..domain.subtitle_track import SubtitleTrack
from ..options.mp3_options import MP3_BITRATES
from .size_estimator import estimate_audio_size, estimate_format_size

SKIP_PROTOCOLS = {"mhtml"}
SKIP_EXTENSIONS = {"mhtml"}

_CODEC_LABELS = (
    ("avc1", "H.264"),
    ("h264", "H.264"),
    ("vp9", "VP9"),
    ("vp09", "VP9"),
    ("av01", "AV1"),
    ("mp4a", "AAC"),
    ("opus", "Opus"),
)

# Compatibility beats efficiency for a file the user will play anywhere.
_CODEC_RANK = {"H.264": 3, "VP9": 2, "AV1": 1}


class FormatNormalizer:
    def build(self, info: dict) -> tuple[FormatCatalogue, list[SubtitleTrack]]:
        duration = info.get("duration") or 0
        usable = [f for f in (info.get("formats") or []) if self._is_usable(f)]
        return (
            FormatCatalogue(
                video=self._video_options(usable, duration),
                audio=self._audio_options(usable, duration),
            ),
            self._subtitles(info),
        )

    # ----------------------------------------------------------------- video
    def _video_options(self, formats: list[dict], duration: float) -> list[VideoOption]:
        best_audio = self._best_audio(formats)
        audio_size = (
            estimate_format_size(best_audio, duration)[0] if best_audio else 0
        ) or 0

        buckets: dict[tuple[int, bool], tuple[tuple, VideoOption]] = {}
        for fmt in formats:
            if fmt.get("vcodec") in (None, "none") or not fmt.get("height"):
                continue

            height = int(fmt["height"])
            is_high_fps = (fmt.get("fps") or 0) > 30
            key = (height, is_high_fps)

            codec = self._codec_label(fmt.get("vcodec"))
            rank = (_CODEC_RANK.get(codec, 0), fmt.get("tbr") or 0)
            if key in buckets and rank <= buckets[key][0]:
                continue

            size, is_estimate = estimate_format_size(fmt, duration)
            progressive = fmt.get("acodec") not in (None, "none")
            total = None
            if size is not None:
                total = size if progressive else size + audio_size

            buckets[key] = (
                rank,
                VideoOption(
                    id=f"video:{height}:{'60' if is_high_fps else '30'}",
                    height=height,
                    label=f"{height}p{'60' if is_high_fps else ''}",
                    fps=fmt.get("fps"),
                    video_codec=codec,
                    audio_codec="AAC",
                    container="mp4",
                    needs_merge=not progressive,
                    size_bytes=total,
                    size_is_estimate=is_estimate or not progressive,
                    requires_po_token=self._needs_po_token(fmt),
                ),
            )

        options = [option for _, option in buckets.values()]
        return sorted(options, key=lambda o: (-o.height, -(o.fps or 0)))

    # ----------------------------------------------------------------- audio
    def _audio_options(self, formats: list[dict], duration: float) -> list[AudioOption]:
        options = [
            AudioOption(
                id=f"audio:mp3:{bitrate}",
                label=f"MP3 {bitrate} kbps",
                container="mp3",
                codec="MP3",
                bitrate_kbps=bitrate,
                size_bytes=estimate_audio_size(bitrate, duration),
                size_is_estimate=True,
            )
            for bitrate in sorted(MP3_BITRATES, reverse=True)
        ]

        best_audio = self._best_audio(formats)
        if best_audio:
            size, is_estimate = estimate_format_size(best_audio, duration)
            options.append(
                AudioOption(
                    id="audio:original",
                    label="Original audio (no re-encode)",
                    container=best_audio.get("ext") or "m4a",
                    codec=self._codec_label(best_audio.get("acodec")),
                    bitrate_kbps=int(best_audio["abr"]) if best_audio.get("abr") else None,
                    size_bytes=size,
                    size_is_estimate=is_estimate,
                    is_passthrough=True,
                )
            )
        return options

    # ------------------------------------------------------------- subtitles
    def _subtitles(self, info: dict) -> list[SubtitleTrack]:
        """Manual and auto-generated tracks are shown as separate groups.

        ASR quality is visibly worse, so conflating them misleads the user.
        """
        tracks: list[SubtitleTrack] = []
        for lang, entries in (info.get("subtitles") or {}).items():
            tracks.append(SubtitleTrack(lang=lang, label=self._lang_label(lang, entries), is_auto=False))
        for lang, entries in (info.get("automatic_captions") or {}).items():
            if any(t.lang == lang and not t.is_auto for t in tracks):
                continue
            tracks.append(SubtitleTrack(lang=lang, label=self._lang_label(lang, entries), is_auto=True))
        return sorted(tracks, key=lambda t: (t.is_auto, t.lang))

    # ------------------------------------------------------------- internals
    def _is_usable(self, fmt: dict) -> bool:
        if fmt.get("protocol") in SKIP_PROTOCOLS or fmt.get("ext") in SKIP_EXTENSIONS:
            return False
        if fmt.get("format_note") == "storyboard":
            return False
        if fmt.get("has_drm"):
            return False
        if fmt.get("vcodec") in (None, "none") and fmt.get("acodec") in (None, "none"):
            return False
        return True

    def _best_audio(self, formats: list[dict]) -> dict | None:
        candidates = [
            f
            for f in formats
            if f.get("acodec") not in (None, "none") and f.get("vcodec") in (None, "none")
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda f: f.get("abr") or f.get("tbr") or 0)

    def _codec_label(self, codec: str | None) -> str:
        value = (codec or "").lower()
        for prefix, label in _CODEC_LABELS:
            if value.startswith(prefix):
                return label
        return value.split(".")[0].upper() or "Unknown"

    def _needs_po_token(self, fmt: dict) -> bool:
        return "missing_pot" in (fmt.get("format_note") or "").lower()

    def _lang_label(self, lang: str, entries: list) -> str:
        for entry in entries or []:
            if entry.get("name"):
                return entry["name"]
        return lang
