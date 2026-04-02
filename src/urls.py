from django.contrib import admin
from django.urls import include, path
from core.views import MetricsView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    path("metrics/", MetricsView.as_view()),
]
