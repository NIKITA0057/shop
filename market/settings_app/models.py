"""
Модуль для работы с настройками сайта.

Этот модуль содержит классы и функции для работы с настройками сайта,
включая модель `SiteSettings` для хранения основных настроек сайта.
"""

import os
from typing import Dict, Any

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .singleton_model import (
    SingletonModel,
    BANNERS_EXPIRATION_TIME,
    FAILED_IMPORTS_DIR,
    SUCCESSFUL_IMPORTS_DIR,
    DOCS_DIR,
    FIXTURE_DIR,
    PAGINATE_PRODUCTS_BY,
)


def get_default_email_settings() -> Dict[str, Any]:
    """
    Получает настройки доступа к почте по умолчанию из переменных окружения.

    Returns:
        Dict[str, Any]: Словарь с настройками доступа к почте.
    """
    return {
        "EMAIL_HOST": os.getenv("EMAIL_HOST", ""),
        "EMAIL_USE_TLS": os.getenv("EMAIL_USE_TLS", ""),
        "EMAIL_USE_SSL": os.getenv("EMAIL_USE_SSL", ""),
        "EMAIL__HOST_PORT": os.getenv("EMAIL_HOST_PORT", ""),
        "EMAIL_HOST_USER": os.getenv("EMAIL_HOST_USER", ""),
        "EMAIL_HOST_PASSWORD": os.getenv("EMAIL_HOST_PASSWORD", ""),
    }


class ProjectSettingsManager(models.Manager):
    """
    Менеджер модели `SiteSettings`.

    Этот менеджер предоставляет дополнительные методы для работы с объектами `SiteSettings`.
    """

    def get_instance(self):
        """
        Получает или создает экземпляр настроек сайта.

        Если в базе данных уже существует экземпляр настроек сайта, возвращает его.
        В противном случае создает новый экземпляр и возвращает его.
        """
        if self.exists():
            return self.first()
        return self.create()


class SiteSettings(SingletonModel):
    """
    Модель настроек сайта.

    Эта модель содержит настройки сайта, такие как директории документов,
    настройки доступа к почте и другие параметры.
    """

    docs_dir = models.CharField(
        max_length=255, default=DOCS_DIR, verbose_name=_("Директория документов")
    )  # Директория для хранения документов
    successful_imports_dir = models.CharField(
        max_length=255, default=SUCCESSFUL_IMPORTS_DIR, verbose_name=_("Директория успешных импортов")
    )  # Директория для успешных импортов
    failed_imports_dir = models.CharField(
        max_length=255, default=FAILED_IMPORTS_DIR, verbose_name=_("Директория неудачных импортов")
    )  # Директория для неудачных импортов
    fixture_dir = models.CharField(max_length=255, default=FIXTURE_DIR, verbose_name=_("Директория фикстур"))
    banners_expiration_time = models.PositiveIntegerField(
        default=BANNERS_EXPIRATION_TIME, verbose_name=_("Время истечения баннеров")
    )  # Время истечения баннеров (в секундах)
    email_access_settings = models.JSONField(
        default=get_default_email_settings,
        verbose_name=_("настройки e-mail"),
        help_text="Email access settings from .env",
    )
    paginate_products_by = models.PositiveIntegerField(
        default=PAGINATE_PRODUCTS_BY, verbose_name=_("количество товаров на странице")
    )  # Количество товаров на странице при отображении списка

    objects = ProjectSettingsManager()

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Переопределенный метод сохранения для модели SiteSettings.
        """
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """
        Возвращает URL для просмотра или редактирования настроек сайта.
        """
        if self.pk:
            return reverse("settings_app:sitesettings_change", kwargs={"pk": self.pk})
        else:
            return reverse("settings_app:sitesettings_add")

    class Meta:
        """
        Метаданные класса SiteSettings
        """

        verbose_name = _("настройки сайта")
        verbose_name_plural = _("настройки сайта")
