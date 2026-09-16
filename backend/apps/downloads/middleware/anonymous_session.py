"""Attach an anonymous identity to every request.

The identity is a *signed* cookie rather than a client-supplied id. A bare
UUID would let anyone claim another session's jobs; signing means only the
server can mint one, which makes ``filter(session=...)`` a real authorisation
boundary. ``httpOnly`` keeps it out of reach of page scripts.

The cookie is host-only: it is sent to the API and never read by the page, so
scoping it to the whole domain would widen it for no benefit.

The salted IP hash is the backstop, because cookies are clearable.
"""

import hashlib
import uuid

from django.conf import settings
from django.core import signing

SALT = "yetpanda.anon-session"


class AnonymousSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        session_id, issued = self._resolve(request)
        request.anon_session_id = session_id
        request.client_ip = self._client_ip(request)
        request.client_ip_hash = self._hash(request.client_ip)

        response = self.get_response(request)

        if issued:
            response.set_cookie(
                settings.ANON_SESSION_COOKIE,
                signing.dumps({"sid": session_id}, salt=SALT),
                max_age=settings.ANON_SESSION_MAX_AGE,
                secure=True,
                httponly=True,
                samesite="None",
                path="/",
            )
        return response

    def _resolve(self, request) -> tuple[str, bool]:
        raw = request.COOKIES.get(settings.ANON_SESSION_COOKIE)
        if raw:
            try:
                payload = signing.loads(
                    raw, salt=SALT, max_age=settings.ANON_SESSION_MAX_AGE
                )
                return payload["sid"], False
            except (signing.BadSignature, KeyError, TypeError):
                pass
        return str(uuid.uuid4()), True

    def _client_ip(self, request) -> str:
        """Trust only REMOTE_ADDR, which the proxy sets.

        Reading ``X-Forwarded-For[0]`` would be spoofable, letting one caller
        mint unlimited identities and defeat every IP-keyed limit.
        """
        return request.META.get("REMOTE_ADDR", "") or "0.0.0.0"

    def _hash(self, ip: str) -> str:
        return hashlib.sha256(f"{ip}{settings.IP_HASH_SALT}".encode()).hexdigest()[:32]
