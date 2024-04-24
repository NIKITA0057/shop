"""
Пакет config содержит настройки и конфигурации для проекта Django.
"""

from config.celery import celery_app as celery_app

__all__ = ("celery_app",)
