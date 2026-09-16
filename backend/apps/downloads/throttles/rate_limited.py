"""Guards that apply a named rate limit before a view runs."""

from rest_framework.permissions import BasePermission

from apps.extraction.domain.error_code import ErrorCode
from apps.extraction.domain.exceptions import PolicyError

from ..services.rate_limiter import RateLimiter


class RateLimited(BasePermission):
    """Base guard. Subclasses name the limit they enforce."""

    limit_name: str = ""

    def has_permission(self, request, view) -> bool:
        result = RateLimiter().check(
            self.limit_name,
            getattr(request, "anon_session_id", ""),
            getattr(request, "client_ip_hash", ""),
        )
        if not result.allowed:
            raise PolicyError(
                ErrorCode.QUOTA_EXCEEDED,
                f"{self.limit_name} limit, retry in {result.retry_after}s",
            )
        return True


class ProbeRateLimited(RateLimited):
    limit_name = "probe"


class JobCreateRateLimited(RateLimited):
    limit_name = "job_create"


class BatchCreateRateLimited(RateLimited):
    limit_name = "batch_create"


class PollRateLimited(RateLimited):
    limit_name = "poll"
