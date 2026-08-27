"""The fair dispatcher.

Celery cannot do per-tenant fairness: its Redis "priority" is a bucket-of-
lists hack and it has no notion of a tenant, so a 200-item playlist would
starve every other user. Postgres is therefore the queue of record, and this
task decides what actually reaches Celery.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="downloads.dispatch_ready_jobs", ignore_result=True)
def dispatch_ready_jobs() -> int:
    from ..dispatch.fair_dispatcher import FairDispatcher

    return FairDispatcher().dispatch()
