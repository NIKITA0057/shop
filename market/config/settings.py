"""Модуль настроек проекта."""

import gettext
import os
import pathlib
from pathlib import Path

import dj_database_url
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from jinja2.ext import Extension
from jinja2.ext import i18n

load_dotenv(os.path.join("..", ".env"))

BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_ROOT = os.path.join(BASE_DIR, "uploads")
MEDIA_URL = "/uploads/"

CART_SESSION_ID = "cart"

SECRET_KEY = "django-insecure-=e-i4dlx_qq&ra7un4)u8bdr#08q)gc_*yyy4@7--kt(0(p#!("

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_jinja",
    "django_filters",
    "django_extensions",
    "products",
    "shops",
    "accounts",
    "cart",
    "imports",
    "settings_app",
    "order",
    "comparison",
    "django_celery_beat",
    "django_celery_results",
    "discounts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

ROOT_URLCONF = "config.urls"

LOCALE_PATHS = [
    pathlib.Path(__file__).resolve().parents[1] / "locale",
]

LANGUAGE_CODE = "ru"
LANGUAGES = [
    ("ru", _("Русский")),
    ("en", _("Английский")),
]

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

USE_L10N = True

jinja_env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=True,
    extensions=[i18n],
)

jinja_env.add_extension("jinja2.ext.debug")


class DjangoTranslationExtension(Extension):
    def __init__(self, environment):
        super(DjangoTranslationExtension, self).__init__(environment)
        environment.globals["_"] = gettext


TEMPLATES = [
    {
        "BACKEND": "django_jinja.backend.Jinja2",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            # django-jinja defaults
            "match_extension": ".jinja2",
            "match_regex": None,
            "app_dirname": "templates",
            "constants": {},
            "environment": "jinja2.Environment",
            "globals": {
                "all_categories": "templatetags.globals.get_categories",
            },
            "context_processors": [
                "context_processors.cart_context.get_cart_cost",
                "django.contrib.messages.context_processors.messages",
                "context_processors.comparison_context.comparison_count",
                "django.template.context_processors.i18n",
            ],
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {"default": dj_database_url.parse(os.getenv("DATABASE_URL"))}

REDIS_URL = os.getenv("REDIS_URL")

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

AUTH_USER_MODEL = "accounts.User"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
LOGIN_REDIRECT_URL = reverse_lazy("user:main")
STATIC_URL = "static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
FIXTURE_DIRS = [
    os.path.join(BASE_DIR, "fixtures"),
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CELERY_BROKER_URL = REDIS_URL
CELERY_TASK_TRACK_STARTED = True
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BROKER_TRANSPORT_OPTION = {"visibility_timeout": 3600}
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_DEFAULT_QUEUE = "default"
