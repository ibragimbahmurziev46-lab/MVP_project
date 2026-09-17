from django.contrib import admin

from .models import Material



   

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    """Управление библиотекой материалов (раздел 15 ТЗ)."""

    list_display = (
        "title",
        "user",
        "subject",
        "grade",
        "material_type",
        "is_published",
        "created_at",

        
    )
    list_filter = ("material_type", "subject", "grade", "is_published")
    search_fields = ("title",)
    date_hierarchy = "created_at"

    @admin.action(description="Опубликовать в библиотеке")
    def make_published(self, request, queryset):
        queryset.update(is_published=True)

    actions = ("make_published",)