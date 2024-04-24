"""Тесты приложения discounts"""

from django.test import TestCase

from discounts.models import DiscountProduct, DiscountSet, DiscountCart


class DiscountProductModelTest(TestCase):
    """Класс для тестирования модели скидок на продукты"""

    fixtures = ["05-categories.json", "06-tags.json", "07-products.json", "09-discounts_product.json"]

    def test_fixture_loading(self) -> None:
        """Тест загрузки фикстур"""
        discount_products_count: int = DiscountProduct.objects.count()
        self.assertEqual(discount_products_count, 5)

    def test_name_max_length(self) -> None:
        """Тест ограничения на длину названия скидки"""
        discount: DiscountProduct = DiscountProduct.objects.get(pk=1)
        max_length: int = discount._meta.get_field("title").max_length
        self.assertEqual(max_length, 100)


class DiscountSetModelTest(TestCase):
    """Класс для тестирования модели скидок на продукты"""

    fixtures = ["05-categories.json", "06-tags.json", "07-products.json", "10-discounts_set.json"]

    def test_fixture_loading(self) -> None:
        """Тест загрузки фикстур"""
        discount_set_count: int = DiscountSet.objects.count()
        self.assertEqual(discount_set_count, 5)

    def test_name_max_length(self) -> None:
        """Тест ограничения на длину названия скидки"""
        discount: DiscountSet = DiscountSet.objects.get(pk=1)
        max_length: int = discount._meta.get_field("title").max_length
        self.assertEqual(max_length, 100)


class DiscountCartModelTest(TestCase):
    """Класс для тестирования модели скидок на стоимость корзины"""

    fixtures = [
        "11-discounts_cart.json",
    ]

    def test_fixture_loading(self) -> None:
        """Тест загрузки фикстур"""
        discount_cart_count: int = DiscountCart.objects.count()
        self.assertEqual(discount_cart_count, 5)

    def test_name_max_length(self) -> None:
        """Тест ограничения на длину названия скидки"""
        discount: DiscountCart = DiscountCart.objects.get(pk=1)
        max_length: int = discount._meta.get_field("title").max_length
        self.assertEqual(max_length, 100)
