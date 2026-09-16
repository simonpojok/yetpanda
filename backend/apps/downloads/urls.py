"""API routes, mounted at /v1/ by config.urls (no /api prefix)."""

from django.urls import path

from .views import (
    BatchArchiveView,
    BatchCreateView,
    BatchDetailView,
    BatchRetryView,
    FileServeView,
    JobCollectionView,
    JobDetailView,
    PlatformListView,
    ProbeView,
)

app_name = "downloads"

urlpatterns = [
    path("platforms", PlatformListView.as_view(), name="platform-list"),
    path("probe", ProbeView.as_view(), name="probe"),
    path("jobs", JobCollectionView.as_view(), name="job-collection"),
    path("jobs/<uuid:job_id>", JobDetailView.as_view(), name="job-detail"),
    path("batches", BatchCreateView.as_view(), name="batch-create"),
    path("batches/<uuid:batch_id>", BatchDetailView.as_view(), name="batch-detail"),
    path("batches/<uuid:batch_id>/retry", BatchRetryView.as_view(), name="batch-retry"),
    path(
        "batches/<uuid:batch_id>/archive.zip",
        BatchArchiveView.as_view(),
        name="batch-archive",
    ),
    path(
        "files/<uuid:job_id>/<str:token>/<path:filename>",
        FileServeView.as_view(),
        name="file-serve",
    ),
]
