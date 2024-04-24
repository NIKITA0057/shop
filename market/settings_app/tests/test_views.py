from typing import Dict

from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import User
from settings_app.models import SiteSettings


class SettingsViewTestCase(TestCase):
    """
    Тесты представления для просмотра и изменения настроек.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """
        Настройка перед запуском тестов.
        """
        cls.user = User.objects.create_superuser(username="admin", email="admin@example.com", password="admin")
        cls.client = Client()

    def test_settings_view(self) -> None:
        """
        Тест просмотра и изменения настроек.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse("settings_app:sitesettings_add"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "settings_app/settings.html")

        # Тестирование POST-запроса
        data: Dict[str, object] = {
            "docs_dir": "docs",
            "successful_imports_dir": "successful_imports",
            "failed_imports_dir": "failed_imports",
            "banners_expiration_time": 600,
            "email_access_settings": {},
            "email_credentials": {},
        }
        response = self.client.post(reverse("settings_app:sitesettings_add"), data)
        self.assertEqual(response.status_code, 200)  # Перенаправление на admin:index при успешном сохранении
        self.assertEqual(SiteSettings.objects.first().docs_dir, "docs")


class ResetCacheViewTestCase(TestCase):
    """
    Тесты представления для сброса кэша.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """
        Настройка перед запуском тестов.
        """
        cls.client = Client()
        cls.user = User.objects.create_superuser(username="test_user", email="test@example.com", password="password")
        cls.client.force_login(cls.user)  # Используйте force_login для аутентификации пользователя

    def test_reset_cache_view(self) -> None:
        """
        Тест сброса кэша.
        """
        # Тестирование GET-запроса
        response = self.client.get(reverse("settings_app:reset_cache"))
        self.assertEqual(response.status_code, 302)  # Ожидается перенаправление

        # Тестирование POST-запроса
        response = self.client.post(reverse("settings_app:reset_cache"))
        self.assertEqual(response.status_code, 302)  # Ожидается перенаправление
