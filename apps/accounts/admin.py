from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Администрирование пользователей (по ТЗ раздел 15)."""

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Персональные данные",
            {"fields": ("first_name", "last_name", "school", "city")},
        ),
        (
            "Права",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_display = ("email", "first_name", "last_name", "school", "city", "is_staff")
    search_fields = ("email", "first_name", "last_name", "school")
    ordering = ("email",)