"""Утилиты рендера AI-шаблонов.

Шаблоны хранятся в базе (MaterialType) и используют переменные вида
{{grade}}, {{subject}}, {{topic}}, {{duration}} (раздел 16 ТЗ).
"""

from django.template import Context, Template


def render_template(text: str, **variables) -> str:
    """Подставляет {{переменные}} в текст шаблона.

    Отсутствующие переменные рендерятся как пустая строка (без ошибки).
    """
    if not text:
        return ""
    try:
        return Template(text).render(Context(variables, autoescape=False))
    except Exception:
        # Никогда не роняем генерацию из-за ошибки в шаблоне админа.
        return text


def build_user_message(material_type, variables: dict) -> str:
    """Формирует USER-сообщение: шаблон + параметры + структура документа."""
    parts = []
    rendered = material_type.render_user_prompt(**variables)
    if rendered:
        parts.append(rendered)

    structure = material_type.structure or []
    if structure:
        structure_text = "\n".join(
            f"{i}. {item}" for i, item in enumerate(structure, start=1)
        )
        parts.append("Структура документа:\n" + structure_text)

    return "\n\n".join(p for p in parts if p.strip())


def build_system_message(material_type) -> str:
    base = material_type.system_prompt or (
        "Ты образовательный методист. Не изменяй класс и дисциплину."
    )
    default = (
        "\n\nОтвечай строго в HTML-разметке (без обёртки <html>/<head>/<body>)."
        "Разрешённые теги: <h1> <h2> <h3> <p> <ul> <ol> <li> <table> <thead> "
        "<tbody> <tr> <th> <td> <strong> <em> <br>. Используй только "
        "перечисленные теги и пиши текст на русском языке."
    )
    if default in base:
        return base
    return base + default