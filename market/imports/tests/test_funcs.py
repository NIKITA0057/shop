import unittest
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from imports.common_utils import process_import_common


class TestProcessImportCommon(unittest.TestCase):
    @patch("os.makedirs")
    @patch("builtins.open", create=True)
    @patch("accounts.models.User.objects.get")
    @patch("settings_app.models.SiteSettings.load")
    @patch("imports.common_utils.get_user_shop")
    @patch("imports.common_utils.create_product_and_offer")
    @patch("imports.models.ImportLog.objects.filter")
    def test_process_import_common_with_data(
        self,
        mock_import_log_filter: MagicMock,
        mock_create_product_and_offer: MagicMock,
        mock_get_user_shop: MagicMock,
        mock_site_settings_load: MagicMock,
        mock_user_objects_get: MagicMock,
        mock_open: MagicMock,
        mock_os_makedirs: MagicMock,
    ) -> None:
        """
        Тестирование функции process_import_common при наличии данных.

        Args:
            mock_import_log_filter (MagicMock): Мок объекта фильтрации логов импорта.
            mock_create_product_and_offer (MagicMock): Мок функции создания товара и предложения.
            mock_get_user_shop (MagicMock): Мок функции получения магазина пользователя.
            mock_site_settings_load (MagicMock): Мок загрузки настроек сайта.
            mock_user_objects_get (MagicMock): Мок функции получения пользователя.
            mock_open (MagicMock): Мок функции открытия файла.
            mock_os_makedirs (MagicMock): Мок функции создания директории.

        Returns:
            None
        """
        # Настройка моков
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_shop = MagicMock()  # Мок атрибута магазина
        mock_user.shop = mock_shop
        mock_user_objects_get.return_value = mock_user

        mock_site_settings = MagicMock()
        mock_site_settings.docs_dir = "/docs"
        mock_site_settings.successful_imports_dir = "successful_imports"
        mock_site_settings.failed_imports_dir = "failed_imports"
        mock_site_settings_load.return_value = mock_site_settings

        mock_get_user_shop.return_value = MagicMock()  # Мок магазина

        # Мок загрузки файла с предоставленными данными
        file_content = (
            "name,main_category,subcategory,description,details,tags,price,remains\n"
            'Samsung A50,Гаджеты,Смартфоны,Отличный смартфон,"Диагональ экрана, дм",'
            '5,Цвет,белый,Страна-производитель,Корея,"смартфон, samsung",18000,10\n'
        )
        uploaded_file = SimpleUploadedFile("test.csv", file_content.encode())

        # Вызов функции
        result = process_import_common(uploaded_file, 1)

        # Проверки
        mock_create_product_and_offer.assert_called_once()
        mock_open.assert_called_once()
        mock_os_makedirs.assert_called_once()
        self.assertEqual(result, "")
