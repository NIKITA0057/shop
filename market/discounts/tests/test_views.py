"""Тесты представлений приложения discounts"""

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class DiscountListViewTest(TestCase):
    """
    Класс тестирования представления списка скидок
    """

    fixtures = [
        "02-users.json",
        "04-shops.json",
        "05-categories.json",
        "06-tags.json",
        "07-products.json",
        "08-offers.json",
        "09-discounts_product.json",
        "10-discounts_set.json",
        "11-discounts_cart.json",
    ]

    def setUp(self) -> None:
        """
        Настройка клиента для тестов.
        """
        self.test_user: User = User.objects.create_user(username="testuser", password="12345")
        self.client: Client = Client()

    def test_discount_list_view(self) -> None:
        """Тестирование представления списка скидок."""
        response = self.client.get(reverse("discounts:discount-list"))
        self.assertEqual(response.status_code, 200)
        if response.context is not None:
            self.assertTrue("discount_sets" in response.context)
            self.assertEqual(len(response.context["discount_sets"]), 5)
            self.assertTrue("discount_cart" in response.context)
            self.assertEqual(len(response.context["discount_cart"]), 5)
            self.assertTrue("discounts" in response.context)
            self.assertEqual(len(response.context["discounts"]), 5)

    def test_discount_product_detail_view(self) -> None:
        """Тестирование представления детальной страницы скидки на товар"""
        response = self.client.get(reverse("discounts:discount-product-details", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)

    def test_discount_set_detail_view(self) -> None:
        """Тестирование представления детальной страницы скидки на набор товаров"""
        response = self.client.get(reverse("discounts:discount-set-details", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)

    def test_discount_cart_detail_view(self) -> None:
        """Тестирование представления детальной страницы скидки на стоимость корзины"""
        response = self.client.get(reverse("discounts:discount-cart-details", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)
