"""Root URLconf. The API is mounted at /v1/ with no /api prefix."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("v1/", include("apps.downloads.urls")),
]
