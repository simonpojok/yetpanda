"""Hard-delete rows past the retention window."""

from celery import shared_task


@shared_task(name="downloads.purge_old_rows", ignore_result=True)
def purge_old_rows() -> int:
    from ..services.retention import RetentionService

    return RetentionService().purge_old_rows()
