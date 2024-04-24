"""Тесты сервисов приложения discounts"""
from decimal import Decimal

from django.test import TestCase

from discounts.services import calculate_set, calculate_cart, calculate_product_price_with_discount
from products.models import Product


class DiscountSetServiceTest(TestCase):
    """Класс для тестирования сервисов скидок на наборы"""

    fixtures = [
        "02-users.json",
        "04-shops.json",
        "05-categories.json",
        "06-tags.json",
        "07-products.json",
        "08-offers.json",
        "10-discounts_set.json",
    ]

    def test_calculate_set(self) -> None:
        """Тест получения параметром скидки с наибольшим весом"""
        products = Product.objects.filter(pk__in=[8, 9, 11, 23])
        offers = [product.offer_set.first() for product in products]
        weight, discount_amount = calculate_set(offers)
        self.assertEqual(len(offers), 4)
        self.assertEqual(weight, Decimal("0.90"))
        self.assertEqual(discount_amount, 100)


class DiscountCartServiceTest(TestCase):
    """Класс для тестирования сервисов скидок на стоимость корзины"""

    fixtures = [
        "11-discounts_cart.json",
    ]

    def test_calculate_cart(self) -> None:
        """Тест получения параметров скидки на стоимость корзины"""
        price = Decimal(5500)
        weight, percentage = calculate_cart(price)
        self.assertEqual(weight, Decimal("0.85"))
        self.assertEqual(percentage, 50)


class DiscountProductServiceTest(TestCase):
    """Класс для тестирования сервисов скидок на товары"""

    fixtures = [
        "02-users.json",
        "04-shops.json",
        "05-categories.json",
        "06-tags.json",
        "07-products.json",
        "08-offers.json",
        "09-discounts_product.json",
    ]

    def test_calculate_product_price_with_discount(self) -> None:
        """Тест функции для определения стоимости товара со скидкой"""
        product = Product.objects.get(pk=1)
        offer = product.offer_set.first()
        price = calculate_product_price_with_discount(offer)
        self.assertEqual(price, Decimal("1425"))
