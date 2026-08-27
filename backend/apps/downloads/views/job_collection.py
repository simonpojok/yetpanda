"""GET/POST /v1/jobs

One path, two verbs: listing and creation stay in separate classes, this only
binds them to the same route.
"""

from .job_create import JobCreateView
from .job_list import JobListView


class JobCollectionView(JobListView, JobCreateView):
    """GET lists the caller's jobs; POST queues a new one."""
