"""Local development: Caddy terminates TLS for *.yetpanda.dev."""

from .base import *  # noqa: F403

DEBUG = True

# Caddy already serves https only; Django must not redirect again.
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0

# Caddy runs in dev too, so exercise the production file-serving path.
USE_X_ACCEL = env.bool("USE_X_ACCEL", default=True)  # noqa: F405

INTERNAL_IPS = ["127.0.0.1"]
