from django.conf import settings
from django.db import models
from django.urls import reverse

from apps.subjects.models import Grade, MaterialType, Subject


class Material(models.Model):
    """Созданный учителем материал (по ТЗ разделы 13, 17)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="materials",
        on_delete=models.CASCADE,
        verbose_name="пользователь",
    )
    grade = models.ForeignKey(
        Grade, related_name="materials", on_delete=models.PROTECT, verbose_name="класс"
    )
    subject = models.ForeignKey(
        Subject,
        related_name="materials",
        on_delete=models.PROTECT,
        verbose_name="предмет",
    )
    material_type = models.ForeignKey(
        MaterialType,
        related_name="materials",
        on_delete=models.PROTECT,
        verbose_name="тип материала",
    )

    title = models.CharField("название", max_length=255)
    contents = models.JSONField("содержимое", blank=True, default=dict)
    settings = models.JSONField(
        "параметры генерации",
        blank=True,
        default=dict,
        help_text="Пример: {\"lesson_duration\": 45, \"difficulty\": \"medium\", \"questions\": 10}",
    )

    is_published = models.BooleanField(
        "опубликован в библиотеке", default=False
    )
    created_at = models.DateTimeField("создан", auto_now_add=True)
    updated_at = models.DateTimeField("обновлён", auto_now=True)

    class Meta:
        verbose_name = "материал"
        verbose_name_plural = "материалы"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("materials:detail", kwargs={"pk": self.pk})

    def duplicate_for(self, user):
        copy = Material(
            user=user,
            grade=self.grade,
            subject=self.subject,
            material_type=self.material_type,
            title=f"Копия: {self.title}",
            contents=self.contents,
            settings=self.settings,
            is_published=False,
        )
        copy.save()
        return copy