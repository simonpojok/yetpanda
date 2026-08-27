# syntax=docker/dockerfile:1

FROM python:3.12-slim AS base

# ffmpeg does the merging/transcoding; deno is required by yt-dlp since
# 2025.11.12 to solve YouTube's nsig/signature challenges. Without deno the
# web client is silently dropped and extraction degrades.
COPY --from=denoland/deno:bin /deno /usr/local/bin/deno
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg ca-certificates procps \
    && rm -rf /var/lib/apt/lists/*

# Install into the system prefix, not .venv - the dev bind mount would
# otherwise shadow a project-local virtualenv.
ENV UV_PROJECT_ENVIRONMENT=/usr/local \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


FROM base AS dev
RUN uv sync --frozen --no-install-project


FROM base AS prod
RUN python manage.py collectstatic --noinput --settings=config.settings.base || true
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
