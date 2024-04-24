"""
Модуль для настройки и запуска Celery в приложении.

Этот модуль содержит конфигурацию и настройки для Celery, включая расписание задач и
автоматическое обнаружение задач.

"""

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "market.config.settings")

celery_app = Celery("market")

celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    "every": {
        "task": "Установить товар дня",
        "schedule": crontab(hour="0", minute="0"),
    },
}
