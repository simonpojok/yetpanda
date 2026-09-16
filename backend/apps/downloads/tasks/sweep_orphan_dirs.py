"""Reconcile the filesystem against the database.

We delete files before updating rows, so a crash between the two leaks disk.
This is the safety net for the direction we chose.
"""

from celery import shared_task


@shared_task(name="downloads.sweep_orphan_dirs", ignore_result=True)
def sweep_orphan_dirs() -> int:
    from ..services.retention import RetentionService

    return RetentionService().sweep_orphan_dirs()
