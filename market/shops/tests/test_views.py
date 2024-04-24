from typing import Any
from unittest.mock import patch, MagicMock

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils.translation import activate

from accounts.models import User
from shops.models import Shop
from shops.views import ShopView, ShopCreate, ShopRemove


class ShopViewTest(TestCase):
    """Тестирование представления магазина."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Настройка начальных данных для тестирования."""
        cls.factory: RequestFactory = RequestFactory()
        cls.user: User = User.objects.create(username="test_user")
        cls.shop: Shop = Shop.objects.create(user=cls.user, name="Test Shop")

    def test_shop_view_get(self) -> None:
        """Тестирование GET-запроса представления магазина."""
        activate("ru")
        url: str = reverse("shops:shop_dashboard")
        request: Any = self.factory.get(url)
        request.user: User = self.user
        middleware: SessionMiddleware = SessionMiddleware(lambda request: None)
        middleware.process_request(request)
        with patch("cart.views.CartInstance", MagicMock()):
            response: Any = ShopView.as_view()(request)
        self.assertEqual(response.status_code, 200)


class ShopCreateTest(TestCase):
    """Тестирование создания магазина."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Настройка начальных данных для тестирования."""
        cls.factory: RequestFactory = RequestFactory()
        cls.user: User = User.objects.create(username="test_user")

    def test_shop_create_get(self) -> None:
        """Тестирование GET-запроса для создания магазина."""
        activate("ru")
        url: str = reverse("shops:shop_create")
        request: Any = self.factory.get(url)
        request.user: User = self.user
        middleware: SessionMiddleware = SessionMiddleware(lambda request: None)
        middleware.process_request(request)
        with patch("cart.views.CartInstance", MagicMock()):
            response: Any = ShopCreate.as_view()(request)
        self.assertEqual(response.status_code, 200)


class ShopRemoveTest(TestCase):
    """Тестирование удаления магазина."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Настройка начальных данных для тестирования."""
        cls.factory: RequestFactory = RequestFactory()
        cls.user: User = User.objects.create(username="test_user")
        cls.shop: Shop = Shop.objects.create(user=cls.user, name="Test Shop")

    def test_shop_remove_get(self) -> None:
        """Тестирование GET-запроса для удаления магазина."""
        activate("ru")
        url: str = reverse("shops:shop_remove")
        request: Any = self.factory.get(url)
        request.user: User = self.user
        middleware: SessionMiddleware = SessionMiddleware(lambda request: None)
        middleware.process_request(request)
        with patch("cart.views.CartInstance", MagicMock()):
            response: Any = ShopRemove.as_view()(request)
        self.assertEqual(response.status_code, 200)
