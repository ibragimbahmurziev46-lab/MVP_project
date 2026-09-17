"""AI-клиент поверх OpenAI-совместимого API (/v1/chat/completions).

Поддерживает локальные модели (Ollama: http://localhost:11434/v1) и любые
облачные сервисы (OpenRouter, OpenAI и т.д.). Настройки — в settings/.env.
"""

import requests
from django.conf import settings


class AIClientError(Exception):
    """Ошибка обращения к LLM API."""


def chat(
    system: str,
    user: str,
    temperature: float = 0.7,
    max_tokens: int | None = None,
) -> str:
    """Отправляет запрос к модели и возвращает текст ответа."""
    url = settings.AI_BASE_URL.rstrip("/") + "/chat/completions"
    headers = {"Content-Type": "application/json"}
    if settings.AI_API_KEY:
        headers["Authorization"] = f"Bearer {settings.AI_API_KEY}"

    payload = {
        "model": settings.AI_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens or settings.AI_MAX_TOKENS,
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=settings.AI_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise AIClientError(
            f"Не удалось подключиться к AI ({settings.AI_BASE_URL}). "
            f"Проверьте, что сервер запущен. {exc}"
        ) from exc

    if response.status_code != 200:
        raise AIClientError(
            f"AI вернул ошибку {response.status_code}: {response.text[:500]}"
        )

    try:
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, ValueError) as exc:
        raise AIClientError(f"Некорректный ответ AI: {response.text[:500]}") from exc


def is_available() -> bool:
    """Проверяет доступность модели (без полноценного запроса)."""
    if settings.AI_MOCK:
        return False
    try:
        chat("Ты — помощник.", "Ответь одним словом: доступен?", max_tokens=5)
        return True
    except AIClientError:
        return False