"""Stable machine-readable error codes exposed by the API."""

from enum import StrEnum


class ErrorCode(StrEnum):
    # Permanent - the user cannot retry into success.
    INVALID_URL = "invalid_url"
    UNSUPPORTED_HOST = "unsupported_host"
    NOT_FOUND = "not_found"
    PRIVATE = "private"
    MEMBERS_ONLY = "members_only"
    AGE_RESTRICTED = "age_restricted"
    GEO_BLOCKED = "geo_blocked"
    LIVE_NOT_SUPPORTED = "live_not_supported"
    DRM_PROTECTED = "drm_protected"
    TOO_LONG = "too_long"
    TOO_LARGE = "too_large"
    QUOTA_EXCEEDED = "quota_exceeded"
    CANCELLED = "cancelled"

    # Transient - worth another attempt.
    BOT_CHECK = "bot_check"
    THROTTLED = "throttled"
    NETWORK = "network"
    EXTRACTOR_ERROR = "extractor_error"
    POSTPROCESS_FAILED = "postprocess_failed"
    DISK_FULL = "disk_full"
    WORKER_LOST = "worker_lost"
    UNKNOWN = "unknown"


RETRYABLE: frozenset[ErrorCode] = frozenset(
    {
        ErrorCode.BOT_CHECK,
        ErrorCode.THROTTLED,
        ErrorCode.NETWORK,
        ErrorCode.EXTRACTOR_ERROR,
        ErrorCode.DISK_FULL,
        ErrorCode.WORKER_LOST,
    }
)

HTTP_STATUS: dict[ErrorCode, int] = {
    ErrorCode.INVALID_URL: 400,
    ErrorCode.UNSUPPORTED_HOST: 400,
    ErrorCode.LIVE_NOT_SUPPORTED: 400,
    ErrorCode.DRM_PROTECTED: 400,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.PRIVATE: 403,
    ErrorCode.MEMBERS_ONLY: 403,
    ErrorCode.AGE_RESTRICTED: 403,
    ErrorCode.GEO_BLOCKED: 451,
    ErrorCode.TOO_LONG: 413,
    ErrorCode.TOO_LARGE: 413,
    ErrorCode.QUOTA_EXCEEDED: 429,
    ErrorCode.THROTTLED: 503,
    ErrorCode.BOT_CHECK: 503,
    ErrorCode.NETWORK: 503,
    ErrorCode.EXTRACTOR_ERROR: 503,
    ErrorCode.DISK_FULL: 507,
}

USER_MESSAGE: dict[ErrorCode, str] = {
    ErrorCode.INVALID_URL: "That does not look like a YouTube link. Check it and try again.",
    ErrorCode.UNSUPPORTED_HOST: "Only YouTube links work right now. Other platforms are coming soon.",
    ErrorCode.NOT_FOUND: "This video no longer exists.",
    ErrorCode.PRIVATE: "This video is private.",
    ErrorCode.MEMBERS_ONLY: "This video is for channel members only.",
    ErrorCode.AGE_RESTRICTED: "This video is age-restricted and cannot be downloaded.",
    ErrorCode.GEO_BLOCKED: "This video is not available in this region.",
    ErrorCode.LIVE_NOT_SUPPORTED: "Live streams cannot be downloaded. Try again once it ends.",
    ErrorCode.DRM_PROTECTED: "This video is copy-protected.",
    ErrorCode.TOO_LONG: "This video is longer than the limit.",
    ErrorCode.TOO_LARGE: "This file would be larger than the limit. Try a lower quality.",
    ErrorCode.QUOTA_EXCEEDED: "You have hit today's download limit. Try again later.",
    ErrorCode.BOT_CHECK: "YouTube is asking us to verify. Try again in a moment.",
    ErrorCode.THROTTLED: "YouTube is rate-limiting us. Try again in a moment.",
    ErrorCode.NETWORK: "The connection dropped. Try again.",
    ErrorCode.EXTRACTOR_ERROR: "We could not read this video. Try again in a moment.",
    ErrorCode.POSTPROCESS_FAILED: "Converting the file failed. Try a different format.",
    ErrorCode.DISK_FULL: "We are out of space right now. Try again shortly.",
    ErrorCode.WORKER_LOST: "That download was interrupted. Try again.",
    ErrorCode.CANCELLED: "Download cancelled.",
    ErrorCode.UNKNOWN: "Something went wrong. Try again.",
}
