from unittest import TestCase
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory

from products.views import MainPageView


class TestMainPageView(TestCase):
    """Тестирование класса MainPageView."""

    def setUp(self):
        """Настройка теста."""
        self.factory = RequestFactory()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(username="testuser", password="password")
        self.request = self.factory.get("/")
        self.request.user = self.user
        self.main_page_view = MainPageView(request=self.request)
        self.main_page_view.template_name = "products/index.jinja2"

    @patch("products.views.MainPageService")
    def test_get_context_data(self, MockMainPageService):
        """Тестирование метода get_context_data."""
        # Заменяем экземпляр MainPageService на мок
        mock_main_page_service = MockMainPageService.return_value

        # Мокируем метод get_products
        mock_products = ["Product1", "Product2"]
        mock_main_page_service.get_top_products.return_value = mock_products

        # Мокируем метод banners_cache
        mock_banners = ["Banner1", "Banner2"]
        mock_main_page_service.banners_cache.return_value = mock_banners

        # Вызываем тестируемый метод
        context = self.main_page_view.get_context_data()

        # Проверяем, были ли вызваны методы get_products и banners_cache
        mock_main_page_service.get_top_products.assert_called_once()
        mock_main_page_service.banners_cache.assert_called_once()

        # Проверяем, содержит ли контекст ожидаемые данные
        self.assertIn("top_products", context)
        self.assertIn("banners", context)
        self.assertEqual(context["top_products"], mock_products)
        self.assertEqual(context["banners"], mock_banners)
