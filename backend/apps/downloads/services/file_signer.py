"""Short-lived signed URLs for finished files.

The token goes in a path segment rather than a query string: it keeps the
proxy's internal rewrite trivial, and leaves the filename as the last segment,
which browsers use as a download-name fallback.

The token is deliberately *not* bound to the session. People open media in a
new tab or a native player where the cookie will not travel; the ten-minute
expiry is the real boundary, and the URL is regenerated on every poll.
"""

from django.conf import settings
from django.core import signing

SALT = "yetpanda.file"


class FileSigner:
    def sign(self, job_id: str) -> str:
        return signing.dumps({"job": str(job_id)}, salt=SALT)

    def verify(self, token: str, job_id: str) -> bool:
        try:
            payload = signing.loads(token, salt=SALT, max_age=settings.FILE_URL_TTL)
        except signing.BadSignature:
            return False
        return payload.get("job") == str(job_id)

    def build_url(self, job_id: str, filename: str, attachment: bool = False) -> str:
        from urllib.parse import quote

        url = f"/v1/files/{job_id}/{self.sign(job_id)}/{quote(filename)}"
        return f"{url}?dl=1" if attachment else url
