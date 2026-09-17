"""AI-команды внутри редактора (раздел 9 ТЗ).

Сократить, расширить, сделать понятнее, адаптировать для другого класса,
добавить пример, добавить практическое задание, добавить вопросы, проверить ошибки.
"""

from django.conf import settings

from apps.generator.service import sanitize_html

from . import client
from .utils import build_system_message

COMMANDS: dict[str, str] = {
    "shorten": "Сократи следующий текст, сохранив его основное содержание и структуру.",
    "expand": "Расширь следующий текст, добавив подробностей, пояснений и примеров.",
    "simplify": "Сделай следующий текст понятнее для школьников: проще формулировки, короче предложения.",
    "adapt": "Адаптируй следующий текст для другого класса (если класс указан — учитывай его уровень).",
    "example": "Добавь к тексту наглядный пример по теме.",
    "task": "Добавь к тексту практическое задание с местом для ответа.",
    "questions": "Добавь к тексту вопросы ученикам для проверки понимания.",
    "check": "Проверь текст на фактические и грамматические ошибки и верни исправленную версию.",
}


def run_ai_command(content_html: str, command: str, extra: str = "") -> str:
    """Применяет AI-команду к содержимому и возвращает обновлённый HTML."""
    if command not in COMMANDS:
        raise ValueError(f"Неизвестная команда: {command}")

    instructions = COMMANDS[command]
    if extra:
        instructions += f"\nДополнительно: {extra}"

    if settings.AI_MOCK:
        return sanitize_html(content_html)

    system = (
        "Ты образовательный методист, помогаешь учителю редактировать материал."
        "\nОтвечай строго в HTML-разметке (без обёртки <html>/<head>/<body>)."
        " Разрешённые теги: <h1> <h2> <h3> <p> <ul> <ol> <li> <table> <thead> "
        "<tbody> <tr> <th> <td> <strong> <em> <br>. Пиши на русском языке."
    )
    user = f"{instructions}\n\nВот текущее содержимое материала:\n```\n{content_html}\n```"

    try:
        raw = client.chat(system, user)
    except client.AIClientError:
        # AI недоступен — возвращаем текст без изменений
        return sanitize_html(content_html)

    return sanitize_html(raw)