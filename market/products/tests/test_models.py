from django.test import TestCase

from products.models import Product, Category, Tag, Banner


class ProductModelTest(TestCase):
    """Класс для тестирования модели продукта"""

    fixtures = [
        "05-categories.json",
        "06-tags.json",
        "07-products.json",
    ]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.product = Product.objects.get(pk=1)

    def test_fixture_loading(self) -> None:
        products_count = Product.objects.count()
        self.assertEqual(products_count, 53)

    def test_name_max_length(self) -> None:
        max_length = self.product._meta.get_field("name").max_length
        self.assertEqual(max_length, 100)


class CategoryModelTest(TestCase):
    """Класс для тестирования модели категории"""

    fixtures = ["05-categories.json"]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.category = Category.objects.get(pk=1)

    def test_fixture_loading(self) -> None:
        category_count = Category.objects.count()
        self.assertEqual(category_count, 20)

    def test_name_max_length(self) -> None:
        max_length = self.category._meta.get_field("name").max_length
        self.assertEqual(max_length, 512)


class TagModelTest(TestCase):
    """Класс для тестирования модели тега"""

    fixtures = ["06-tags.json"]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.tag = Tag.objects.get(pk=1)

    def test_fixture_loading(self) -> None:
        tag_count = Tag.objects.count()
        self.assertEqual(tag_count, 35)

    def test_name_max_length(self) -> None:
        max_length = self.tag._meta.get_field("name").max_length
        self.assertEqual(max_length, 100)


class BannerModelTest(TestCase):
    """Класс для тестирования модели баннера"""

    fixtures = ["15-banners.json"]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.banner = Banner.objects.get(pk=1)

    def test_fixture_loading(self) -> None:
        banners_count = Banner.objects.count()
        self.assertEqual(banners_count, 4)

    def test_verbose_name(self) -> None:
        banner = self.banner
        field_verboses = {"name": "названия", "actual": "актуальность", "preview": "превью", "link": "ссылка"}
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(banner._meta.get_field(field).verbose_name, expected_value)
