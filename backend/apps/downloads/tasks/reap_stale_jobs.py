"""Recover jobs whose worker died without saying so."""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="downloads.reap_stale_jobs", ignore_result=True)
def reap_stale_jobs() -> int:
    from ..services.retention import RetentionService

    return RetentionService().reap_stale_jobs()
