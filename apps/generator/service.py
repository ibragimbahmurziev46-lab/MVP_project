"""Сервис генерации: параметры пользователя → промпт → AI/fallback → документ.

Реализует связку «шаблон + данные пользователя + AI» (раздел 9 ТЗ).
Ошибки генерации перехватываются, и вызывающий код получает корректное
сообщение для пользователя (критерий приёмки MVP).
"""

import logging
from html.parser import HTMLParser

from django.conf import settings

from apps.ai import client as ai_client
from apps.ai import fallback
from apps.ai.utils import build_system_message, build_user_message

logger = logging.getLogger(__name__)

ALLOWED_TAGS = {
    "h1", "h2", "h3", "p", "ul", "ol", "li",
    "table", "thead", "tbody", "tr", "th", "td",
    "strong", "em", "br", "img",
}


class _HtmlSanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ALLOWED_TAGS:
            attrs_html = ""
            if tag == "img":
                attrs_dict = dict(attrs)
                src = attrs_dict.get("src", "").strip()
                if src:
                    attrs_html = f' src="{src}" alt="изображение"'
            self.parts.append(f"<{tag}{attrs_html}>")

    def handle_endtag(self, tag):
        if tag in ALLOWED_TAGS:
            self.parts.append(f"</{tag}>")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        self.parts.append(data)


def sanitize_html(raw_html: str) -> str:
    """Оставляет только безопасные теги, остальное — как текст."""
    if not raw_html:
        return ""
    parser = _HtmlSanitizer()
    try:
        parser.feed(raw_html)
        parser.close()
    except Exception:
        logger.exception("Ошибка при санитизации HTML ответа AI")
        return raw_html
    return "".join(parser.parts).strip()


def generate_html(material_type, params: dict) -> str:
    """Генерирует HTML-содержимое материала по типу и параметрам.

    Приоритет: AI (если доступен и не включён AI_MOCK) → fallback-шаблон.
    AI-ответ всегда проходит санитизацию.
    """
    if settings.AI_MOCK:
        return fallback.generate(material_type.slug, params)

    try:
        variables = fallback._params_to_prompt_vars(params)
        system = build_system_message(material_type)
        user = build_user_message(material_type, variables)
        raw = ai_client.chat(system, user)
        return sanitize_html(raw)
    except ai_client.AIClientError as exc:
        logger.warning("AI недоступен, применяю fallback-шаблон: %s", exc)
        return fallback.generate(material_type.slug, params)
    except Exception as exc:
        logger.exception("Неожиданная ошибка генерации")
        raise exc


def create_material_content(material_type, params: dict) -> dict:
    """Возвращает содержимое материала в виде {"html": ...}."""
    return {"html": generate_html(material_type, params)}