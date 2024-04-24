"""Тесты сервисов приложения products"""
import datetime

from django.test import TestCase

from products.services.catalog_services import relative_url
from products.services.mainpage_services import MainPageService


class CatalogServicesTest(TestCase):
    """Класс для тестирования сервисов страницы каталога"""

    def test_relative_url_without_page_parameter(self) -> None:
        """Тест метода получения относительного url с параметрами"""
        url = "/catalog?param1=1&param2=2"
        res, are_params = relative_url(url)
        self.assertTrue(are_params)
        self.assertEqual(res, "/catalog?param1=1&param2=2")

    def test_relative_url_with_page_parameter(self) -> None:
        """Тест метода получения относительного url с параметрами"""
        url = "/catalog?page=1&param1=1&param2=2"
        res, are_params = relative_url(url)
        self.assertTrue(are_params)
        self.assertEqual(res, "/catalog?param1=1&param2=2")

    def test_relative_url_without_parameters(self) -> None:
        """Тест метода получения относительного url с параметрами"""
        url = "/catalog"
        res, are_params = relative_url(url)
        self.assertFalse(are_params)
        self.assertEqual(res, "/catalog")


class MainPageServicesTest(TestCase):
    """Класс для тестирования сервисов главной страницы"""

    def setUp(self) -> None:
        today = datetime.datetime.today()
        one_day = datetime.timedelta(days=1)
        self.tomorrow = today + one_day

    def test_get_midnight_tomorrow(self):
        main_page_services = MainPageService()
        next_day = main_page_services.get_tomorrow_date()

        self.assertEqual(next_day.day, self.tomorrow.day)
