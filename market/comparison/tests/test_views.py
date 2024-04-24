from typing import Any
from unittest.mock import patch, MagicMock

from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, RequestFactory

from accounts.models import User
from comparison.views import ComparisonView, add_to_comparison, remove_from_comparison_view


class ComparisonViewTestCase(TestCase):
    """
    Класс тестирования представления сравнения.
    """

    def setUp(self) -> None:
        """
        Настройка тестов.
        """
        self.factory: RequestFactory = RequestFactory()
        self.user: User = User.objects.create_user(username="testuser", password="12345")

    def test_get_comparison_view(self) -> None:
        """
        Тестирование метода GET представления сравнения.
        """
        request: Any = self.factory.get("/comparison/")
        request.user = self.user
        request.session = {}
        setattr(request, "_messages", FallbackStorage(request))
        response: Any = ComparisonView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    @patch("comparison.views.add_to_comparison_service")
    def test_add_to_comparison_view(self, mock_add_to_comparison_service: Any) -> None:
        """
        Тестирование метода добавления в сравнение.
        """
        mock_add_to_comparison_service.return_value = (True, True)
        request: Any = self.factory.post("/add-to-comparison/1/")
        request.user = self.user
        request.session = {}
        middleware: Any = MessageMiddleware(lambda r: None)
        middleware.process_request(request)
        setattr(request, "_messages", FallbackStorage(request))
        response: Any = add_to_comparison(request, product_id="1")
        self.assertEqual(response.status_code, 302)

    @patch("comparison.views.remove_from_comparison")
    def test_remove_from_comparison_view(self, mock_remove_from_comparison: Any) -> None:
        """
        Тестирование метода удаления из сравнения.
        """
        mock_remove_from_comparison.return_value = True
        request: Any = self.factory.post("/remove-from-comparison/")
        request.user = self.user
        request.session = {}
        request.POST = {"product_id": "1"}
        middleware: Any = MessageMiddleware(lambda r: None)
        middleware.process_request(request)
        setattr(request, "_messages", FallbackStorage(request))
        response: Any = remove_from_comparison_view(request)
        self.assertEqual(response.status_code, 302)


# Тестирование автономных функций
@patch("comparison.views.add_to_comparison_service")
def test_add_to_comparison_function(mock_add_to_comparison_service: Any) -> None:
    """
    Тестирование функции добавления в сравнение.
    """
    mock_add_to_comparison_service.return_value = (True, True)
    request: MagicMock = MagicMock()
    request.user = User.objects.create_user(username="testuser", password="12345")
    add_to_comparison(request, product_id="1")
    mock_add_to_comparison_service.assert_called_once_with(request.user, "1")


@patch("comparison.views.remove_from_comparison")
def test_remove_from_comparison_function(mock_remove_from_comparison: Any) -> None:
    """
    Тестирование функции удаления из сравнения.
    """
    mock_remove_from_comparison.return_value = True
    request: MagicMock = MagicMock()
    request.user = User.objects.create_user(username="testuser", password="12345")
    request.POST = {"product_id": "1"}
    remove_from_comparison_view(request)
    mock_remove_from_comparison.assert_called_once_with(request.user, "1")
