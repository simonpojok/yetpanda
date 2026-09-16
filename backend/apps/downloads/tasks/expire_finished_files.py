"""Delete finished files past their TTL."""

from celery import shared_task


@shared_task(name="downloads.expire_finished_files", ignore_result=True)
def expire_finished_files() -> int:
    from ..services.retention import RetentionService

    return RetentionService().expire_finished_files()
