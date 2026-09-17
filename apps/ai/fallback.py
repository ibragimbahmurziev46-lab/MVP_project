"""Fallback-генератор материалов из встроенных шаблонов.

Используется, когда LLM недоступен (или включён AI_MOCK), чтобы основной
сценарий «выбор → генерация → экспорт» всегда работал. Также используется
в тестах (критерий приёмки MVP: ошибки генерации обрабатываются корректно).
"""

import random

LESSON_STAGES = [
    ("Организационный этап", "Приветствует учащихся, проверяет готовность к уроку, фиксирует отсутствующих."),
    ("Актуализация знаний", "Организует повторение опорных знаний, связывает новый материал с изученным."),
    ("Изучение нового материала", "Излагает тему, организует работу с источником, задаёт вопросы."),
    ("Закрепление", "Предлагает задания на применение полученных знаний, разбирает ошибки."),
    ("Рефлексия", "Подводит итоги, выясняет степень усвоения, даёт обратную связь."),
]

DIFFICULTY_LABEL = {"easy": "лёгкая", "medium": "средняя", "hard": "сложная"}


def _params_to_prompt_vars(params: dict) -> dict:
    """Собирает словарь для подстановки в шаблон MaterialType."""
    subject = params.get("subject", "")
    if hasattr(subject, "name"):
        subject = subject.name
    return {
        "grade": params.get("grade", ""),
        "subject": subject,
        "topic": params.get("topic", ""),
        "duration": params.get("duration", ""),
    }


def lesson_plan(params: dict) -> str:
    topic = params.get("topic") or "Тема урока"
    grade = params.get("grade", "")
    subject = params.get("subject", "")
    if hasattr(subject, "name"):
        subject = subject.name
    duration = params.get("duration") or 45
    lesson_type = params.get("lesson_type") or "изучение нового материала"
    blocks = params.get("blocks") or []

    rows = []
    for name, teacher_actions in LESSON_STAGES:
        rows.append(
            "<tr>"
            f"<td>{name}</td>"
            f"<td>5 мин</td>"
            f"<td>{teacher_actions}</td>"
            f"<td>Слушают, отвечают на вопросы, выполняют задания.</td>"
            "</tr>"
        )
    stage_table = (
        "<table><thead><tr><th>Этап</th><th>Время</th>"
        "<th>Действия учителя</th><th>Действия учащихся</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )

    extra = ""
    if "цели урока" in blocks:
        extra += "<h3>Цели урока</h3><ul><li>Познакомить учащихся с новой темой.</li><li>Сформировать умения применять полученные знания.</li></ul>"
    if "планируемые результаты" in blocks:
        extra += "<h3>Планируемые результаты</h3><ul><li>Предметные: понимают ключевые понятия темы.</li><li>Метапредметные: умеют работать с информацией.</li><li>Личностные: проявляют интерес к предмету.</li></ul>"
    if "домашнее задание" in blocks:
        extra += "<h3>Домашнее задание</h3><p>Прочитать параграф по теме, ответить на вопросы в конце параграфа, выполнить задание в рабочей тетради.</p>"
    if "рефлексия" in blocks:
        extra += "<h3>Рефлексия</h3><p>Ученики оценивают, что было понятно, а что вызвало трудности, заполняя «лестницу успеха».</p>"

    return (
        f"<h2>{topic}</h2>"
        f"<p>Класс: <strong>{grade}</strong> · Предмет: <strong>{subject}</strong> · "
        f"Тип урока: <em>{lesson_type}</em> · "
        f"Длительность: <strong>{duration} минут</strong></p>"
        f"<h3>Вводная часть</h3><p>Урок по теме «{topic}» направлен на формирование "
        f"у учащихся целостного представления о предмете изучения.</p>"
        f"{extra}"
        f"<h3>Этапы урока</h3>{stage_table}"
        f"<h3>Домашнее задание</h3><p>Проработать конспект урока, подготовиться к следующему занятию.</p>"
    )


def test(params: dict) -> str:
    topic = params.get("topic") or "Тема теста"
    questions = int(params.get("questions") or 5)
    difficulty = DIFFICULTY_LABEL.get(params.get("difficulty"), "средняя")

    prompts = [
        ("Что относится к основным понятиям темы?", ["Понятие А", "Понятие Б", "Понятие В"], 0),
        ("Какое из утверждений верно?", ["Утверждение 1", "Утверждение 2", "Утверждение 3"], 1),
        ("Приведите пример, иллюстрирующий тему.", None, None),
    ]
    items = []
    for i in range(questions):
        title, options, correct = prompts[i % len(prompts)]
        title = f"{i + 1}. {title}"
        if options:
            items.append(f"<h3>{title}</h3><ul>" + "".join(f"<li>{o}</li>" for o in options) + "</ul>")
        else:
            items.append(f"<h3>{title}</h3><p>Письменный ответ.</p>")

    return (
        f"<h2>Тест: {topic}</h2>"
        f"<p>Класс: <strong>{params.get('grade', '')}</strong> · "
        f"Предмет: <strong>{params.get('subject', '')}</strong> · "
        f"Сложность: <em>{difficulty}</em> · Количество вопросов: <strong>{questions}</strong></p>"
        + "".join(items)
        + "<h3>Ответы для учителя</h3><p>Демонстрационные — проверяются по ключу.</p>"
    )


def worksheet(params: dict) -> str:
    topic = params.get("topic") or "Тема рабочего листа"
    return (
        f"<h2>Рабочий лист: {topic}</h2>"
        f"<p>Класс: <strong>{params.get('grade', '')}</strong> · "
        f"Предмет: <strong>{params.get('subject', '')}</strong></p>"
        "<h3>Краткая теория</h3><p>Запишите главное по теме. Основные понятия и определения.</p>"
        "<h3>Примеры</h3><ul><li>Пример 1 с пояснением.</li><li>Пример 2 с пояснением.</li></ul>"
        "<h3>Задания</h3><ol><li>Простое задание (2–3 минуты).</li>"
        "<li>Задание средней сложности (5–7 минут).</li>"
        "<li>Задание повышенной сложности (*).</li></ol>"
        "<h3>Место для ответа</h3><p>______________________________________</p><p>______________________________________</p>"
    )


def presentation(params: dict) -> str:
    topic = params.get("topic") or "Тема презентации"
    slides = int(params.get("slides") or 7)
    style = params.get("style") or "минималистичный"
    return (
        f"<h2>Презентация: {topic}</h2>"
        f"<p>Класс: <strong>{params.get('grade', '')}</strong> · "
        f"Предмет: <strong>{params.get('subject', '')}</strong> · "
        f"Стиль: <em>{style}</em> · Слайдов: <strong>{slides}</strong></p>"
        f"<p><strong>Структура презентации:</strong></p><ol>"
        + "".join(f"<li>Слайд {i}: изображение раздела {i} темы.</li>" for i in range(1, slides + 1))
        + "</ol>"
    )


GENERATORS = {
    "lesson_plan": lesson_plan,
    "поурочный_план": lesson_plan,
    "test": test,
    "тест": test,
    "worksheet": worksheet,
    "рабочий_лист": worksheet,
    "presentation": presentation,
    "презентация": presentation,
}


def generate(slug: str, params: dict) -> str:
    """Возвращает HTML-контент материала по слагу типа (или универсальный)."""
    func = GENERATORS.get(slug)
    if func is None:
        topic = params.get("topic") or "Материал"
        return (
            f"<h2>{topic}</h2><p>Класс: <strong>{params.get('grade', '')}</strong> · "
            f"Предмет: <strong>{params.get('subject', '')}</strong></p>"
            "<p>Содержимое этого типа материала будет сформировано после подключения AI.</p>"
        )
    return func(params)