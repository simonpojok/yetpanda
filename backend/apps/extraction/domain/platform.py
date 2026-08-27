"""A supported (or soon-to-be-supported) source platform."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Platform:
    id: str
    name: str
    available: bool
    hostnames: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "available": self.available}
