"""Turn the signed cookie on a request into a persisted Session row."""

from ..models import Session


class SessionResolver:
    def resolve(self, request) -> Session:
        """The middleware has already validated the signature."""
        session, _ = Session.objects.get_or_create(
            id=request.anon_session_id,
            defaults={"ip_hash": request.client_ip_hash},
        )
        if session.ip_hash != request.client_ip_hash:
            Session.objects.filter(pk=session.pk).update(ip_hash=request.client_ip_hash)
            session.ip_hash = request.client_ip_hash
        return session
