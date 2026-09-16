"""Celery application.

Queue split matters: probes are interactive and must never queue behind a
40-minute download, so they run on their own workers. The download queue is
fed exclusively by the fair dispatcher, never directly by the API.
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("yetpanda")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.update(
    task_default_queue="maint",
    task_routes={
        "downloads.probe_source": {"queue": "probe"},
        "downloads.expand_playlist": {"queue": "expand"},
        "downloads.run_download": {"queue": "download"},
        "downloads.*": {"queue": "maint"},
    },
    # Redis has no native ack, so kombu redelivers anything un-acked after
    # visibility_timeout. With hour-long downloads that would *duplicate* a
    # legitimately-running job onto a second worker. We ack early and recover
    # crashes with our own reaper, which also has to clean temp files anyway.
    task_acks_late=False,
    task_reject_on_worker_lost=False,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    result_backend=None,
    beat_schedule={
        "dispatch-ready-jobs": {
            "task": "downloads.dispatch_ready_jobs",
            "schedule": 1.0,
            "options": {"queue": "maint", "expires": 5},
        },
        "reap-stale-jobs": {
            "task": "downloads.reap_stale_jobs",
            "schedule": 60.0,
            "options": {"queue": "maint"},
        },
        "expire-finished-files": {
            "task": "downloads.expire_finished_files",
            "schedule": 300.0,
            "options": {"queue": "maint"},
        },
        "sweep-orphan-dirs": {
            "task": "downloads.sweep_orphan_dirs",
            "schedule": 900.0,
            "options": {"queue": "maint"},
        },
        "purge-old-rows": {
            "task": "downloads.purge_old_rows",
            "schedule": 3600.0,
            "options": {"queue": "maint"},
        },
    },
)

app.autodiscover_tasks()
