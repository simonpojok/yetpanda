"""An available caption track."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SubtitleTrack:
    lang: str
    label: str
    is_auto: bool

    def as_dict(self) -> dict:
        return {"lang": self.lang, "label": self.label, "is_auto": self.is_auto}
