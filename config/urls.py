"""URL configuration for the teacher portal project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter

from apps.materials.api import (
    GradeViewSet,
    MaterialTypeViewSet,
    MaterialViewSet,
    SubjectViewSet,
)

router = DefaultRouter()
router.register("grades", GradeViewSet, basename="grade")
router.register("subjects", SubjectViewSet, basename="subject")
router.register("material-types", MaterialTypeViewSet, basename="material-type")
router.register("materials", MaterialViewSet, basename="material")

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="generator:home", permanent=False)),
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("create/", include("apps.generator.urls")),
    path("materials/", include("apps.materials.urls")),
    path("library/", include("apps.library.urls")),
    # REST API (раздел 14 ТЗ)
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])