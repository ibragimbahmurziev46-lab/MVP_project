"""
Django settings for the teacher portal project.

Tech stack per the technical specification:
- Python 3.13, Django 6.x
- Django REST Framework (API), SQLite for dev / PostgreSQL for prod
- Tailwind CSS (CDN), TipTap editor (CDN)
- AI: OpenAI-compatible LLM API (Ollama / OpenRouter / etc.)
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load variables from .env if present
load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    value = os.environ.get(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-&ffj&zgsdq1+hf+7g6vy_x@m(zm5g4*9^g^n9%v5+bfu!6_yu5",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_bool("DJANGO_DEBUG", True)

ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost,0.0.0.0,[::1],testserver"
)

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    # Project apps
    "apps.accounts",
    "apps.subjects",
    "apps.materials",
    "apps.generator",
    "apps.ai",
    "apps.exports",
    "apps.library",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# dev: SQLite; production: switch to PostgreSQL (structure is ORM-compatible)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# PostgreSQL configuration (uncomment for production):
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.environ.get("POSTGRES_DB", "teacher_portal"),
#         "USER": os.environ.get("POSTGRES_USER", "teacher"),
#         "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
#         "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
#         "PORT": os.environ.get("POSTGRES_PORT", "5432"),
#     }
# }

# Use a custom user model (email login + school/city profile fields)
AUTH_USER_MODEL = "accounts.User"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files (uploaded images etc.)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Auth
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "generator:home"
LOGOUT_REDIRECT_URL = "accounts:login"

# Email (console backend for dev)
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# ---------------------------------------------------------------------------
# AI configuration
#
# The AI client talks to any OpenAI-compatible chat completions endpoint:
#   /v1/chat/completions
#
# Default: local Ollama (http://localhost:11434/v1)
# e.g. `ollama pull qwen3:27b`, then the portal uses AI_MODEL.
# For cloud providers (OpenRouter, OpenAI, etc.) set AI_BASE_URL + AI_API_KEY.
# ---------------------------------------------------------------------------

AI_BASE_URL = os.environ.get("AI_BASE_URL", "http://localhost:11434/v1")
AI_MODEL = os.environ.get("AI_MODEL", "qwen3:27b")
AI_API_KEY = os.environ.get("AI_API_KEY", "")
AI_MAX_TOKENS = int(os.environ.get("AI_MAX_TOKENS", "4000"))
AI_TIMEOUT = int(os.environ.get("AI_TIMEOUT", "120"))

# If True, the generator always uses built-in templates (no LLM call).
AI_MOCK = env_bool("AI_MOCK", False)