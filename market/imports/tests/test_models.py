from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from imports.models import ImportLog, ImportLogProduct, ImportStatus
from products.models import Product, Category

User = get_user_model()


class ImportLogModelTest(TestCase):
    """
    Тестовый класс для модели ImportLog.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """
        Подготовка данных перед запуском тестов.
        """
        cls.user: User = User.objects.create_user(username="testuser", password="testpassword")
        cls.import_log: ImportLog = ImportLog.objects.create(
            user=cls.user, file_name="test_file.txt", status=ImportStatus.COMPLETED, timestamp=timezone.now()
        )

    def test_import_log_str(self) -> None:
        """
        Тестирование метода __str__ модели ImportLog.

        Ожидаемое поведение: Строковое представление должно быть правильно отформатировано.
        """
        expected_str: str = f"Импорт: {self.import_log.file_name}, Статус: {self.import_log.get_status_display()}"
        self.assertEqual(str(self.import_log), expected_str, msg="Неправильное представление __str__.")

    def test_verbose_name(self) -> None:
        """
        Тестирование verbose_name и verbose_name_plural модели ImportLog.

        Ожидаемое поведение: Названия должны быть установлены правильно.
        """
        self.assertEqual(ImportLog._meta.verbose_name, "лог импорта", msg="Неправильное verbose_name.")
        self.assertEqual(ImportLog._meta.verbose_name_plural, "логи импорта", msg="Неправильное verbose_name_plural.")


class ImportLogProductModelTest(TestCase):
    """
    Тестовый класс для модели ImportLogProduct.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """
        Подготовка данных перед запуском тестов.
        """
        cls.user: User = User.objects.create_user(username="testuser", password="testpassword")
        cls.import_log: ImportLog = ImportLog.objects.create(
            user=cls.user, file_name="test_file.txt", status=ImportStatus.COMPLETED, timestamp=timezone.now()
        )
        cls.category: Category = Category.objects.create(name="Test Category")
        cls.product: Product = Product.objects.create(name="Test Product", category=cls.category)

        cls.import_log_product: ImportLogProduct = ImportLogProduct.objects.create(
            import_log=cls.import_log, product=cls.product
        )

    def test_import_log_product_relationships(self) -> None:
        """
        Тестирование отношений модели ImportLogProduct.

        Ожидаемое поведение: Отношения между ImportLogProduct, ImportLog и Product должны быть установлены правильно.
        """
        self.assertEqual(self.import_log_product.import_log, self.import_log, msg="Неправильное отношение ImportLog.")
        self.assertEqual(self.import_log_product.product, self.product, msg="Неправильное отношение Product.")

    def test_verbose_name(self) -> None:
        """
        Тестирование verbose_name и verbose_name_plural модели ImportLogProduct.

        Ожидаемое поведение: Названия должны быть установлены правильно.
        """
        self.assertEqual(
            ImportLogProduct._meta.verbose_name, "продукт в логе импорта", msg="Неправильное verbose_name."
        )
        self.assertEqual(
            ImportLogProduct._meta.verbose_name_plural,
            "продукты в логах импорта",
            msg="Неправильное verbose_name_plural.",
        )
