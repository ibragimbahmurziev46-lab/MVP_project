from django.urls import path

from . import views

app_name = "materials"

urlpatterns = [
    path("", views.material_list, name="list"),
    path("export/<int:pk>/<str:fmt>/", views.material_export, name="export"),
    path("duplicate/<int:pk>/", views.material_duplicate, name="duplicate"),
    path("ai-command/<int:pk>/", views.material_ai_command, name="ai_command"),
    path("<int:pk>/", views.material_detail, name="detail"),
]