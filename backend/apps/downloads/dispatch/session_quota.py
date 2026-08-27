"""How many concurrent downloads one anonymous session may hold."""

from django.conf import settings


class SessionQuota:
    """Caps are enforced at dispatch time, not by blocking workers.

    Blocking a worker on a quota check wastes a slot; refusing to dispatch
    leaves the job in Postgres where it costs nothing and stays cancellable.
    """

    @property
    def per_session_slots(self) -> int:
        return settings.PER_SESSION_SLOTS

    @property
    def global_slots(self) -> int:
        return settings.GLOBAL_DOWNLOAD_SLOTS
