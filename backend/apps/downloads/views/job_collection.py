"""GET/POST /v1/jobs

One path, two verbs. Listing and creation stay in separate classes; this only
binds them to the same route.

The rate limit has to be chosen per method rather than per class: polling runs
at 120/min while creation is capped at 10/min, and inheriting a single
`permission_classes` would silently apply the looser of the two to both.
"""

from ..throttles import JobCreateRateLimited, PollRateLimited
from .job_create import JobCreateView
from .job_list import JobListView


class JobCollectionView(JobListView, JobCreateView):
    """GET lists the caller's jobs; POST queues a new one."""

    def get_permissions(self):
        limit = PollRateLimited if self.request.method == "GET" else JobCreateRateLimited
        return [limit()]
