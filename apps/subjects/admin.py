from django.contrib import admin

from .models import Grade, MaterialType, Subject


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("number", "name")
    ordering = ("number",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active", "order")


@admin.register(MaterialType)
class MaterialTypeAdmin(admin.ModelAdmin):
    """Управление типами материалов и AI-шаблонами (разделы 15–16 ТЗ)."""

    list_display = ("name", "slug", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active", "order")

    fieldsets = (
        (
            "Основное",
            {"fields": ("name", "slug", "is_active", "order")},
        ),
        (
            "AI-шаблоны",
            {
                "fields": (
                    "system_prompt",
                    "user_template",
                    "structure",
                    "required_fields",
                    "variables",
                )
            },
        ),
    )