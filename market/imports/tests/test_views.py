import uuid
from typing import Any

from django.test import TestCase
from django.urls import reverse
from django.utils.translation import activate

from accounts.models import User
from imports.models import ImportLog, ImportLogProduct
from products.models import Product, Category


class ImportDetailsViewTest(TestCase):
    """
    Тестовый класс для представления деталей импорта.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """
        Настройка данных для тестов.
        """
        cls.user_email: str = f"testuser_{uuid.uuid4()}@example.com"
        cls.user: User = User.objects.create_user(username="testuser", password="testpassword", email=cls.user_email)
        cls.import_log: ImportLog = ImportLog.objects.create(user=cls.user)
        cls.category: Category = Category.objects.create(name="Some Category")

    def test_import_details_view(self) -> None:
        """
        Тестирование GET-запроса для представления деталей импорта.
        """
        response: Any = self.client.get(reverse("imports:import-details"), follow=True)
        self.assertRedirects(
            response,
            reverse("accounts:login") + "?next=" + reverse("imports:import-details"),
            target_status_code=200,
        )

    def test_authenticated_user_access(self) -> None:
        """
        Тестирование доступа для аутентифицированного пользователя.
        """

        # Аутентификация пользователя
        self.client.login(username="testuser", password="testpassword")

        # Отправка GET-запроса для представления деталей импорта
        response: Any = self.client.get(reverse("imports:import-details"), follow=True)

        # Проверка, что ответ перенаправляет на страницу входа
        self.assertRedirects(
            response,
            reverse("accounts:login") + "?next=" + reverse("imports:import-details"),
        )

    def test_unauthenticated_user_access(self) -> None:
        """
        Тестирование доступа для неаутентифицированного пользователя.
        """

        # Отправка GET-запроса для представления деталей импорта
        response: Any = self.client.get(reverse("imports:import-details"), args=[self.import_log.id], follow=True)

        # Проверка, что ответ перенаправляет на страницу входа
        self.assertRedirects(
            response,
            reverse("accounts:login") + "?next=" + reverse("imports:import-details"),
        )

    def test_import_counts(self) -> None:
        """
        Тестирование импорта количества.
        """

        # Создание некоторых продуктов
        some_product: Product = Product.objects.create(name="Some Product", category=self.category)
        another_product: Product = Product.objects.create(name="Another Product", category=self.category)

        # Создание импорта продуктов для журнала импорта
        ImportLogProduct.objects.create(import_log=self.import_log, product=some_product)
        ImportLogProduct.objects.create(import_log=self.import_log, product=another_product)

        # Аутентификация пользователя
        self.client.login(username="testuser", password="testpassword")

        # Отправка GET-запроса для представления деталей импорта
        response: Any = self.client.get(reverse("imports:import-details"), follow=True)

        # Проверка, что код статуса ответа равен 200
        self.assertEqual(response.status_code, 200)


class DownloadCSVTemplateViewTest(TestCase):
    """
    Класс тестирования представления скачивания шаблона CSV-файла.
    """

    def setUp(self) -> None:
        # Активация желаемого языка перед запуском тестов
        activate("ru")

    def test_download_csv_template_view(self) -> None:
        """
        Тестирование GET-запроса для скачивания шаблона CSV-файла.

        Ожидается, что не аутентифицированный пользователь будет перенаправлен на страницу входа.
        """
        response: Any = self.client.get(reverse("imports:download-csv-template"))  # noqa
        expected_url: str = reverse("accounts:login") + "?next=" + reverse("imports:download-csv-template")  # noqa
