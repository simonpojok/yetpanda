"""Domain exceptions. Pure Python - no Django, no DRF."""

from .error_code import HTTP_STATUS, RETRYABLE, USER_MESSAGE, ErrorCode


class YetPandaError(Exception):
    """Base for every error the API turns into a structured response."""

    def __init__(self, code: ErrorCode, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}" if detail else str(code))

    @property
    def message(self) -> str:
        return USER_MESSAGE.get(self.code, USER_MESSAGE[ErrorCode.UNKNOWN])

    @property
    def retryable(self) -> bool:
        return self.code in RETRYABLE

    @property
    def http_status(self) -> int:
        return HTTP_STATUS.get(self.code, 500)


class UnsupportedUrlError(YetPandaError):
    """The URL is not a YouTube video or playlist we are willing to fetch."""


class ExtractionError(YetPandaError):
    """yt-dlp could not read the source."""


class PolicyError(YetPandaError):
    """The request is well-formed but violates a limit."""


class DownloadCancelledError(YetPandaError):
    def __init__(self, detail: str = "") -> None:
        super().__init__(ErrorCode.CANCELLED, detail)
