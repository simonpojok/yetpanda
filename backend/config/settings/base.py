"""Settings shared by every environment. Secrets come from the environment."""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-only-insecure-key-replace-in-prod")
DEBUG = False

SITE_DOMAIN = env("SITE_DOMAIN", default="yetpanda.dev")
API_DOMAIN = env("API_DOMAIN", default="api.yetpanda.dev")

# Extra hostnames the same deployment answers to. *.localhost resolves to
# loopback in every browser without an /etc/hosts entry, which makes local
# testing work out of the box while staying genuinely cross-origin.
EXTRA_API_HOSTS = env.list("EXTRA_API_HOSTS", default=[])

# Full origins including scheme. Deriving these from a bare hostname means
# guessing http vs https, and guessing wrong fails as an opaque CORS error.
EXTRA_SITE_ORIGINS = env.list("EXTRA_SITE_ORIGINS", default=[])

ALLOWED_HOSTS = [API_DOMAIN, *EXTRA_API_HOSTS, "127.0.0.1", "localhost"]
CSRF_TRUSTED_ORIGINS = [
    f"https://{SITE_DOMAIN}",
    f"https://www.{SITE_DOMAIN}",
    f"https://{API_DOMAIN}",
    *EXTRA_SITE_ORIGINS,
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "apps.extraction",
    "apps.downloads",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.downloads.middleware.anonymous_session.AnonymousSessionMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": env.db_url(
        "DATABASE_URL",
        default="postgres://yetpanda:yetpanda@127.0.0.1:5434/yetpanda",
    )
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://127.0.0.1:6380/1"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------- cross-origin
CORS_ALLOWED_ORIGINS = [
    f"https://{SITE_DOMAIN}",
    f"https://www.{SITE_DOMAIN}",
    *EXTRA_SITE_ORIGINS,
]
CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = [
    "Content-Range",
    "Content-Length",
    "Accept-Ranges",
    "Content-Disposition",
    "ETag",
]

# Deliberately host-only. The anonymous cookie is read by the API and never
# by page scripts, so widening it to the whole domain would only broaden the
# blast radius - and it would break any hostname that is not SITE_DOMAIN.
SESSION_COOKIE_DOMAIN = None
CSRF_COOKIE_DOMAIN = None
SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# ------------------------------------------------------------------- anonymous
ANON_SESSION_COOKIE = "yp_sid"
ANON_SESSION_MAX_AGE = 60 * 60 * 24 * 30
IP_HASH_SALT = env("IP_HASH_SALT", default="dev-ip-salt")

# ------------------------------------------------------------------ media/jobs
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_WORK_ROOT = MEDIA_ROOT / "work"
MEDIA_DONE_ROOT = MEDIA_ROOT / "done"
USE_X_ACCEL = env.bool("USE_X_ACCEL", default=False)
X_ACCEL_PREFIX = "/_protected/"
FILE_URL_TTL = 600

FFMPEG_PATH = env("FFMPEG_PATH", default="/opt/homebrew/bin/ffmpeg")
YTDLP_CACHE_DIR = BASE_DIR / ".ytdlp-cache"
YTDLP_COOKIEFILE = env("YTDLP_COOKIEFILE", default="")

# --------------------------------------------------------------------- limits
MAX_DURATION_SECONDS = 4 * 60 * 60
MAX_BATCH_ITEM_DURATION_SECONDS = 60 * 60
MAX_FILESIZE_BYTES = 8 * 1024**3
MAX_BATCH_ITEMS = 200
MAX_BATCH_BYTES_VIDEO = 25 * 1024**3
MAX_BATCH_BYTES_AUDIO = 5 * 1024**3
MAX_SESSION_BYTES_PER_DAY = 20 * 1024**3

PER_SESSION_SLOTS = 2
GLOBAL_DOWNLOAD_SLOTS = env.int("GLOBAL_DOWNLOAD_SLOTS", default=4)
DISK_RESERVE_BYTES = 10 * 1024**3
DISK_HIGH_WATERMARK = 0.85
DISK_CRITICAL_WATERMARK = 0.92

JOB_TTL_SECONDS = 2 * 60 * 60
BATCH_TTL_SECONDS = 4 * 60 * 60
ROW_RETENTION_DAYS = 7

MAX_CONCURRENT_ZIPS = 8
ZIP_MAX_BYTES = 5 * 1024**3
ZIP_MAX_ITEMS = 100

# ---------------------------------------------------------------------- celery
CELERY_BROKER_URL = env("REDIS_URL", default="redis://127.0.0.1:6380/0")
CELERY_RESULT_BACKEND = None
CELERY_TASK_ACKS_LATE = False
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_TRACK_STARTED = True
CELERY_BROKER_TRANSPORT_OPTIONS = {"visibility_timeout": 21600}
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "UNAUTHENTICATED_USER": None,
    "EXCEPTION_HANDLER": "apps.downloads.views.exception_handler.api_exception_handler",
}
