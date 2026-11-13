"""Réglages Django du projet Hamac (environnement de développement)."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Clé réservée au développement local : ne jamais l'utiliser en production.
SECRET_KEY = "django-insecure-hamac-dev-only-change-me"

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "leave",
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
        "DIRS": [],
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
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# En développement, les e-mails sont affichés dans la console au lieu d'être envoyés.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "hamac@example.com"

REST_FRAMEWORK = {"DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema"}
SPECTACULAR_SETTINGS = {
    "TITLE": "Hamac API",
    "VERSION": "1.0.0",
    # Le schéma ne décrit pas sa propre route : il reste identique avec ou sans DEBUG.
    "SERVE_INCLUDE_SCHEMA": False,
}

# Journal des requêtes SQL (écrit uniquement quand DEBUG = True).
LOGGING = {
    "version": 1,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "django.db.backends": {"handlers": ["console"], "level": "DEBUG"},
    },
}

# Règles RH : taux des CDD, modifiable sans toucher au code.
HAMAC_FIXED_TERM_DAYS_PER_FULL_MONTH = float(
    os.environ.get("HAMAC_FIXED_TERM_DAYS_PER_FULL_MONTH", "2.08")
)
