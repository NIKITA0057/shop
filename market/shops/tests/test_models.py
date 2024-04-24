import os
from typing import Dict, Any, List

from django.core.serializers import deserialize
from django.db.models import Sum
from django.test import TestCase

from accounts.models import User
from products.models import Product, Category
from settings_app.models import SiteSettings
from shops.models import Shop, Offer


class ShopModelTest(TestCase):
    """Класс для тестирования модели магазина"""

    @classmethod
    def setUpTestData(cls) -> None:
        category: Category = Category.objects.create(name="тестовая категория")
        cls.product: Product = Product.objects.create(
            name="тестовый продукт",
            category=category,
            details={"Диагональ, дм": 101},
        )

        cls.user: User = User.objects.create(username="testuser")
        cls.shop: Shop = Shop.objects.create(name="тестовый магазин", user=cls.user)
        cls.offer: Offer = Offer.objects.create(shop=cls.shop, product=cls.product, price=25)

    def test_verbose_name(self) -> None:
        shop: Shop = ShopModelTest.shop
        field_verboses: Dict[str, str] = {
            "name": "название",
            "products": "товары в магазине",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(shop._meta.get_field(field).verbose_name, expected_value)

    def test_name_max_length(self) -> None:
        shop: Shop = ShopModelTest.shop
        max_length: int = shop._meta.get_field("name").max_length
        self.assertEqual(max_length, 512)


class OfferModelTest(TestCase):
    """Класс для тестирования модели предложения"""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.load_fixtures()

    @classmethod
    def load_fixtures(cls) -> None:
        fixture_dir: str = SiteSettings.load().fixture_dir
        fixtures: List[str] = [
            os.path.join(fixture_dir, "02-users.json"),
            os.path.join(fixture_dir, "04-shops.json"),
            os.path.join(fixture_dir, "05-categories.json"),
            os.path.join(fixture_dir, "06-tags.json"),
            os.path.join(fixture_dir, "07-products.json"),
            os.path.join(fixture_dir, "08-offers.json"),
        ]
        for fixture_file in fixtures:
            with open(fixture_file, "rb") as f:
                for obj in deserialize("json", f):
                    obj.save()

    def setUp(self) -> None:
        super().setUp()
        self.offer: Offer = Offer.objects.get(pk=1)

    def test_verbose_name(self) -> None:
        field_verboses: Dict[str, str] = {
            "price": "цена",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(self.offer._meta.get_field(field).verbose_name, expected_value)

    def test_price_max_digits(self) -> None:
        max_digits: int = self.offer._meta.get_field("price").max_digits
        self.assertEqual(max_digits, 10)

    def test_price_decimal_places(self) -> None:
        decimal_places: int = self.offer._meta.get_field("price").decimal_places
        self.assertEqual(decimal_places, 2)

    def test_fixture_loading(self) -> None:
        remains_products_in_offers: Any = Offer.objects.aggregate(remains_sum=Sum("remains"))["remains_sum"]
        shops_count: int = Shop.objects.count()
        offers_count: int = Offer.objects.count()

        self.assertEqual(remains_products_in_offers, 3808)
        self.assertEqual(shops_count, 8)
        self.assertEqual(offers_count, 139)
