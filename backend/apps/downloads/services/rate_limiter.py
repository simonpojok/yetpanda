"""Redis token buckets, keyed by session *and* IP.

Every limit is evaluated against both keys and the stricter one binds. The
session cookie is the pleasant identifier, but it is clearable - so the salted
IP hash is what actually stops someone farming quota by resetting cookies. IP
budgets are deliberately looser so a shared office NAT is not punished.
"""

import time
from dataclasses import dataclass

from .progress_reporter import get_redis

# Sliding window counter. Cheaper than a true token bucket and accurate
# enough for abuse control, where being off by one request does not matter.
_CONSUME = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local current = redis.call('INCR', key)
if current == 1 then
  redis.call('EXPIRE', key, window)
end
if current > limit then
  return {0, redis.call('TTL', key)}
end
return {1, redis.call('TTL', key)}
"""


@dataclass(frozen=True, slots=True)
class Limit:
    name: str
    session_max: int
    ip_max: int
    window_seconds: int


LIMITS = {
    "probe": Limit("probe", session_max=30, ip_max=60, window_seconds=60),
    "job_create": Limit("job_create", session_max=10, ip_max=20, window_seconds=60),
    "batch_create": Limit("batch_create", session_max=3, ip_max=6, window_seconds=3600),
    "poll": Limit("poll", session_max=120, ip_max=600, window_seconds=60),
}


@dataclass(frozen=True, slots=True)
class RateLimitResult:
    allowed: bool
    retry_after: int


class RateLimiter:
    def __init__(self, redis_client=None) -> None:
        self._redis = redis_client or get_redis()
        self._script = self._redis.register_script(_CONSUME)

    def check(self, name: str, session_id: str, ip_hash: str) -> RateLimitResult:
        limit = LIMITS[name]
        window = self._window(limit.window_seconds)

        for scope, identity, maximum in (
            ("s", session_id, limit.session_max),
            ("i", ip_hash, limit.ip_max),
        ):
            if not identity:
                continue
            key = f"rl:{name}:{scope}:{identity}:{window}"
            allowed, ttl = self._script(keys=[key], args=[maximum, limit.window_seconds])
            if not int(allowed):
                return RateLimitResult(False, max(1, int(ttl)))

        return RateLimitResult(True, 0)

    def _window(self, seconds: int) -> int:
        return int(time.time()) // seconds
