from django.urls import path

from . import views

app_name = "library"

urlpatterns = [
    path("", views.library_list, name="list"),
    path("download/<int:pk>/<str:fmt>/", views.library_download, name="download"),
]