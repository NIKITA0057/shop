"""
Модуль содержит базовые классы и константы, используемые в приложении.
"""
from typing import Dict, Any

from django.db import models


class SingletonModel(models.Model):
    """Базовая модель для реализации синглтона."""

    class Meta:
        """Метаданные класса"""

        abstract: bool = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Переопределенный метод сохранения.

        Удаляет все объекты класса, кроме текущего, перед сохранением.
        """
        self.__class__.objects.exclude(id=self.id).delete()
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> "SingletonModel":
        """
        Загружает экземпляр класса.

        Если экземпляр не найден, создает новый.
        """
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()


DOCS_DIR: str = "docs"  # Директория для хранения документов
SUCCESSFUL_IMPORTS_DIR: str = "successful_imports"  # Директория для успешных импортов
FAILED_IMPORTS_DIR: str = "failed_imports"  # Директория для неудачных импортов
BANNERS_EXPIRATION_TIME: int = 600  # Время истечения баннеров (в секундах)
FIXTURE_DIR: str = "fixtures"  # Директория для фикстур
PAGINATE_PRODUCTS_BY: int = 8  # Количество товаров на странице при отображении списка товаров

# Настройки доступа к электронной почте
EMAIL_ACCESS_SETTINGS: Dict[str, str] = {
    "EMAIL_HOST": "EMAIL_HOST",
    "EMAIL_HOST_USER": "EMAIL_HOST_USER",
    "EMAIL_HOST_PORT": "EMAIL_HOST_PORT",
    "EMAIL_USE_TLS": "EMAIL_USE_TLS",
    "EMAIL_USE_SSL": "EMAIL_USE_SSL",
    "EMAIL_HOST_PASSWORD": "EMAIL_HOST_PASSWORD",
}
