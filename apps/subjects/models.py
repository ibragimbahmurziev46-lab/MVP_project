from django.db import models


class Grade(models.Model):
    """Класс обучения (по ТЗ раздел 13): number 1..11 + название."""

    number = models.PositiveSmallIntegerField("номер класса", unique=True)
    name = models.CharField("название", max_length=64, blank=True)

    class Meta:
        verbose_name = "класс"
        verbose_name_plural = "классы"
        ordering = ["number"]

    def __str__(self):
        return self.name or f"{self.number} класс"

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"{self.number} класс"
        super().save(*args, **kwargs)


class Subject(models.Model):
    """Школьная дисциплина (по ТЗ раздел 13). Админ может скрывать предметы."""

    name = models.CharField("название", max_length=128, unique=True)
    slug = models.SlugField("slug", max_length=128, unique=True)
    is_active = models.BooleanField("активный", default=True)
    order = models.PositiveSmallIntegerField("порядок", default=0)

    class Meta:
        verbose_name = "предмет"
        verbose_name_plural = "предметы"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class MaterialType(models.Model):
    """Тип генерируемого материала (по ТЗ раздел 13).

    Содержит AI-шаблоны и структуру документа. Всё редактируется из
    админки без изменения кода (разделы 15–16 ТЗ).
    """

    name = models.CharField("название", max_length=128, unique=True)
    slug = models.SlugField("slug", max_length=128, unique=True)
    is_active = models.BooleanField("активный", default=True)
    order = models.PositiveSmallIntegerField("порядок", default=0)

    system_prompt = models.TextField(
        "системный промпт",
        blank=True,
        help_text="Задаётся методисту. Пример: «Ты образовательный методист. "
        "Не изменяй класс и дисциплину.»",
    )
    user_template = models.TextField(
        "шаблон USER-сообщения",
        blank=True,
        help_text="Доступные переменные: {{grade}} {{subject}} {{topic}} "
        "{{duration}}. Разделы и параметры подставляются автоматически.",
    )
    structure = models.JSONField(
        "структура документа",
        blank=True,
        default=list,
        help_text="Список разделов документа, которые должны быть в материале.",
    )
    required_fields = models.JSONField(
        "обязательные поля",
        blank=True,
        default=list,
        help_text="Список параметров формы (слаг/имя поля), которые обязательны.",
    )
    variables = models.JSONField(
        "доступные переменные шаблона",
        blank=True,
        default=list,
        help_text="Все переменные, например [\"grade\", \"subject\", \"topic\", \"duration\"].",
    )

    class Meta:
        verbose_name = "тип материала"
        verbose_name_plural = "типы материалов"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def render_user_prompt(self, **kwargs):
        """Подставляет переменные {{var}} в шаблон USER-сообщения."""
        from apps.ai.utils import render_template

        return render_template(self.user_template, **kwargs)