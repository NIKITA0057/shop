"""
Модуль для импорта данных о продуктах и их связанных объектах в систему.

Содержит функции для импорта продуктов, категорий, тегов и предложений магазина в систему из внешних источников.

"""
import logging
import os
from email.mime.multipart import MIMEMultipart
import smtplib
from typing import List, Optional, Tuple
from _csv import reader
from email.mime.text import MIMEText


from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from filelock import FileLock

from accounts.models import User
from products.models import Category, Product, Tag
from settings_app.models import SiteSettings
from shops.models import Offer, Shop
from .models import ImportLog, ImportLogProduct

LOCK_KEY = "import_lock"
LOCK_PATH = "import_lock.lock"
logging.basicConfig(filename="email_errors.log", level=logging.ERROR)


def acquire_lock():
    """
    Получение файлового замка для предотвращения параллельного импорта.
    """
    lock = FileLock(LOCK_PATH)
    with lock:
        cache.set(LOCK_KEY, "locked")


def release_lock():
    """
    Освобождение файлового замка после завершения импорта.
    """
    lock = FileLock(LOCK_PATH)
    with lock:
        cache.delete(LOCK_KEY)


def create_or_update_category(name: str, parent_name: str = None, parent_id: int = None) -> Tuple[Category, bool]:
    """
    Создание или обновление категории.

    Args:
        name (str): Название категории.
        parent_name (str): Название родительской категории.
        parent_id (int): Идентификатор родительской категории.

    Returns:
        Tuple[Category, bool]: Кортеж, содержащий созданную или обновленную категорию и булевое значение,
                              указывающее, была ли она создана.
    """
    parent = None

    try:
        defaults = {}
        if parent_name or parent_id:
            parent_filter = {"name": parent_name} if parent_name else {"id": parent_id}
            parent, _ = Category.objects.get_or_create(**parent_filter)
            defaults["parent"] = parent

        if parent_id is not None and not isinstance(parent_id, int):
            parent_id = int(parent_id)

        sort_index = get_next_sort_index(parent_id)

        category, created = Category.objects.get_or_create(name=name, defaults={"sort_index": sort_index, **defaults})

        if not created:
            for key, value in defaults.items():
                setattr(category, key, value)
            category.save()

        return category, created

    except IntegrityError as e:  # noqa
        return None, False


def get_next_sort_index(parent_id: int = None) -> int:
    """
    Получение следующего доступного индекса сортировки для категории.

    Args:
        parent_id (int): Идентификатор родительской категории.

    Returns:
        int: Следующий доступный индекс сортировки.
    """
    existing_sort_indexes = Category.objects.filter(parent_id=parent_id).values_list("sort_index", flat=True)

    sort_index = 1
    while sort_index in existing_sort_indexes:
        sort_index += 1

    return sort_index


def create_product(
    name: str,
    main_category_name: str,
    subcategory_name: str,
    description: str,
    details: dict,
    tags: List[str],
    import_log_instance: ImportLog,
) -> Product:
    """
    Создание продукта и связанного журнала импорта.

    Args:
        name (str): Название продукта.
        main_category_name (str): Название основной категории продукта.
        subcategory_name (str): Название подкатегории продукта.
        description (str): Описание продукта.
        details (dict): Детали продукта.
        tags (List[str]): Список тегов продукта.
        import_log_instance (ImportLog): Экземпляр журнала импорта.

    Returns:
        Product: Созданный продукт.
    """
    main_category, created_main = create_or_update_category(main_category_name)
    subcategory, created_sub = create_or_update_category(subcategory_name, parent_id=main_category.id)
    category = subcategory if subcategory else main_category

    product = Product.objects.create(name=name, category=category, description=description, details=details)
    product.tags.set(tags)

    import_log_product = ImportLogProduct.objects.create(import_log=import_log_instance, product=product)  # noqa
    import_log_instance.products.add(product)

    return product


def create_product_and_offer(product_data, import_log, user_id):
    """
    Создание продукта и связанного предложения.

    Args:
        product_data: Данные продукта.
        import_log: Экземпляр журнала импорта.
        user_id (int): Идентификатор пользователя.
    """

    (
        name,
        main_category_name,
        subcategory_name,
        description,
        details,
        tags,
        price,
        remains,
    ) = product_data
    main_category, _ = create_or_update_category(main_category_name)
    create_or_update_category(subcategory_name, parent_name=main_category_name)
    tag_objects = [create_or_update_tag(tag) for tag in tags]
    category = create_or_update_category(main_category_name)[0]  # noqa

    existing_product = get_existing_product(name, main_category_name, subcategory_name)

    if existing_product:
        update_existing_product(existing_product, description, details, tag_objects)
        product = existing_product
    else:
        product = create_product(
            name, main_category_name, subcategory_name, description, details, tag_objects, import_log
        )

    import_log_product = ImportLogProduct.objects.create(import_log=import_log, product=product)  # noqa
    import_log.products.add(product)

    shop = get_user_shop(user_id)
    create_or_update_offer(shop, product, price, remains)


def get_existing_product(name: str, main_category_name: str, subcategory_name: str) -> Optional[Product]:
    """
    Получение существующего продукта.

    Args:
        name (str): Название продукта.
        main_category_name (str): Название основной категории продукта.
        subcategory_name (str): Название подкатегории продукта.

    Returns:
        Optional[Product]: Существующий продукт или None, если не найден.
    """
    try:
        main_category, _ = create_or_update_category(main_category_name)
        subcategory, _ = create_or_update_category(subcategory_name, parent_id=main_category.id)
        category = subcategory if subcategory else main_category

        existing_product = Product.objects.get(name=name, category=category)
        return existing_product
    except Product.DoesNotExist:
        return None


def update_existing_product(product: Product, description: str, details: dict, tags: List[Tag]):
    """
    Обновление существующего продукта.

    Args:
        product (Product): Экземпляр существующего продукта.
        description (str): Описание продукта.
        details (dict): Детали продукта.
        tags (List[Tag]): Список тегов продукта.
    """
    product.description = description
    product.details = details
    product.tags.set(tags)
    product.save()


def get_user_shop(user_id: int) -> Shop:
    """
    Получение магазина, связанного с пользователем.

    Args:
        user_id (int): Идентификатор пользователя.

    Returns:
        Shop: Магазин, связанный с пользователем.
    """
    user = User.objects.get(id=user_id)
    return user.shop


def get_shop_name(user_id: int) -> str:
    """
    Получение названия магазина, связанного с пользователем.

    Args:
        user_id (int): Идентификатор пользователя.

    Returns:
        str: Название магазина.
    """
    user = User.objects.get(id=user_id)
    shop = user.shop
    return shop.name


def create_or_update_offer(shop: Shop, product: Product, price: float, remains: int) -> bool:
    """
    Создание или обновление предложения.

    Args:
        shop (Shop): Экземпляр магазина.
        product (Product): Экземпляр продукта.
        price (float): Цена предложения.
        remains (int): Оставшееся количество.

    Returns:
        bool: True, если предложение было создано, False в противном случае.
    """
    offer, created = Offer.objects.get_or_create(
        shop=shop, product=product, defaults={"price": price, "remains": remains}
    )
    return created


def create_or_update_tag(name: str) -> Tag:
    """
    Создание или обновление тега.

    Args:
        name (str): Название тега.

    Returns:
        Tag: Созданный или обновленный тег.
    """
    tag, created = Tag.objects.get_or_create(name=name)
    return tag


def create_import_log(
    file_name: str,
    user: User,
    status: str,
    total_products: int = 0,
    successful_imports: int = 0,
    failed_imports: int = 0,
    error_details: Optional[str] = None,
) -> "ImportLog":
    """
    Создает и сохраняет журнал импорта в базе данных.

    Args:
        file_name (str): Имя файла импорта.
        user (User): Пользователь, выполнивший импорт.
        status (str): Статус импорта.
        total_products (int, optional): Общее количество импортированных продуктов (по умолчанию 0).
        successful_imports (int, optional): Количество успешно импортированных продуктов (по умолчанию 0).
        failed_imports (int, optional): Количество неудачно импортированных продуктов (по умолчанию 0).
        error_details (str, optional): Дополнительные детали об ошибках (по умолчанию None).

    Returns:
        ImportLog: Созданный объект журнала импорта.
    """
    import_log = ImportLog.objects.create(
        file_name=file_name,
        user=user,
        status=status,
        timestamp=timezone.now(),
    )
    import_log.total_products = total_products
    import_log.successful_imports = successful_imports
    import_log.failed_imports = failed_imports
    import_log.error_details = error_details
    import_log.save()
    return import_log


def send_email(sender_email: str, recipient_email: str, subject: str, body: str, site_settings: SiteSettings) -> None:
    """
    Отправляет электронное письмо.

    Args:
        sender_email: Адрес отправителя.
        recipient_email: Адрес получателя.
        subject: Тема письма.
        body: Текст письма.
        site_settings: Настройки сайта для доступа к электронной почте.

    Raises:
        Exception: Если произошла ошибка при отправке письма.
    """
    try:
        email_host = site_settings.email_access_settings.get("EMAIL_HOST", os.getenv("EMAIL_HOST"))
        email_port = site_settings.email_access_settings.get("EMAIL_PORT", os.getenv("EMAIL_HOST_PORT"))

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL(email_host, email_port) as server:
            server.login(
                site_settings.email_access_settings.get("EMAIL_HOST_USER"),
                site_settings.email_access_settings.get("EMAIL_HOST_PASSWORD"),
            )
            server.sendmail(sender_email, recipient_email, message.as_string())
    except Exception as e:  # noqa
        logging.error("An error occurred while sending email:", exc_info=True)


def log_and_notify_error(
    error_message: str, user_id: int, file_name: str, total_products: int, successful_imports: int, failed_imports: int
) -> Optional[str]:
    """
    Журналирует ошибку и отправляет уведомление об ошибке по электронной почте.

    Args:
        error_message: Сообщение об ошибке.
        user_id: Идентификатор пользователя.
        file_name: Имя файла.
        total_products: Общее количество товаров.
        successful_imports: Количество успешных импортов.
        failed_imports: Количество неудачных импортов.

    Returns:
        str: Строка с описанием ошибки, если произошла ошибка; в противном случае None.
    """
    try:
        user = User.objects.get(id=user_id)
        site_settings = SiteSettings.load()
        sender_email = user.email
        recipient_email = site_settings.email_access_settings.get("EMAIL_HOST_USER", os.getenv("EMAIL_HOST_USER"))
        subject = _("Статус импорта от {email}").format(email=user.email)

        body = (
            _("Импорт файла {file_name} завершён с ошибкой.\n").format(file_name=file_name)
            + _("Загружено пользователем: {username} ({email}).\n").format(username=user.username, email=user.email)
            + _("Всего товаров: {total_products}\n").format(total_products=total_products)
            + _("Успешных импортов: {successful_imports}\n").format(successful_imports=successful_imports)
            + _("Неудачных импортов: {failed_imports}").format(failed_imports=failed_imports)
        )

        send_email(sender_email, recipient_email, subject, body, site_settings)

    except Exception as e:
        logging.error("An error occurred while logging and sending email:", exc_info=True)
        return str(e)

    return None


def notify_admin_about_import_success(
    user_id: int, file_name: str, total_products: int, successful_imports: int, failed_imports: int
) -> None:
    """
    Оповещает администратора об успешном импорте по электронной почте.

    Args:
        user_id: Идентификатор пользователя.
        file_name: Имя файла.
        total_products: Общее количество товаров.
        successful_imports: Количество успешных импортов.
        failed_imports: Количество неудачных импортов.
    """
    try:
        user = User.objects.get(id=user_id)
        site_settings = SiteSettings.load()

        sender_email = user.email
        recipient_email = site_settings.email_access_settings.get("EMAIL_HOST_USER", os.getenv("EMAIL_HOST_USER"))
        subject = _("Статус импорта от {email}").format(email=user.email)

        body = (
            _("Импорт файла {file_name} успешно завершен.\n")
            + _("Загружено пользователем: {username} ({email}).\n").format(username=user.username, email=user.email)
            + _("Всего товаров: {total_products}\n").format(total_products=total_products)
            + _("Успешных импортов: {successful_imports}\n").format(successful_imports=successful_imports)
            + _("Неудачных импортов: {failed_imports}").format(failed_imports=failed_imports)
        )

        send_email(sender_email, recipient_email, subject, body, site_settings)

    except Exception as e:  # noqa
        logging.error("An error occurred while sending email:", exc_info=True)


def get_existing_in_progress_import_log(user, file_name):
    """
    Получение существующего журнала импорта, находящегося в процессе выполнения.

    Args:
        user: Экземпляр пользователя.
        file_name (str): Название импортированного файла.

    Returns:
        ImportLog: Существующий журнал импорта в процессе выполнения (или None, если не найден).
    """
    return ImportLog.objects.filter(user=user, file_name=file_name, status="in_progress").first()


def handle_empty_file(file_name, user_id):
    """
    Обработка случая пустого файла.

    Args:
        file_name (str): Название импортированного файла.
        user_id (int): Идентификатор пользователя.

    Returns:
        str: Сообщение об ошибке.
    """
    error_message = _("Загруженный файл пуст")
    return log_and_notify_error(error_message, user_id, file_name, 0, 0, 1)


def handle_failed_import(content, error, file_name, user_id, total_products, successful_imports, failed_imports):
    """
    Обработка случая неудачного импорта.

    Args:
        error: Объект ошибки.
        file_name (str): Название импортированного файла.
        user_id (int): Идентификатор пользователя.
        total_products (int): Общее количество продуктов.
        successful_imports (int): Количество успешных импортов.
        failed_imports (int): Количество неудачных импортов.
    """
    try:
        logging.error("Handling failed import for file: %s", file_name)

        import_log = (
            ImportLog.objects.filter(user_id=user_id, file_name=file_name, status="in_progress")
            .order_by("-id")
            .first()
        )

        if import_log:
            logging.error("Found existing import log for file: %s", file_name)
            import_log.status = "Завершён с ошибкой"
            import_log.error_details = str(error)
            import_log.save()
        else:
            logging.error("Creating new import log for file: %s", file_name)
            import_log = create_import_log(
                file_name=file_name,
                user=User.objects.get(id=user_id),
                status="Завершён с ошибкой",
                total_products=total_products,
                successful_imports=successful_imports,
                failed_imports=failed_imports,
                error_details=str(error),
            )

        new_file_name = f"{import_log.timestamp.strftime('%H-%M-%S_%d-%m-%Y')}_{get_shop_name(import_log.user.id)}.csv"
        site_settings = SiteSettings.load()
        failed_imports_dir = os.path.join(site_settings.docs_dir, site_settings.failed_imports_dir)
        destination_path = os.path.join(failed_imports_dir, new_file_name)

        with open(destination_path, "w", encoding="utf-8") as dest_file:
            dest_file.write(content)

        if import_log.failed_imports == 0:
            notify_admin_about_import_success(
                import_log.user.id,
                new_file_name,
                import_log.total_products,
                import_log.successful_imports,
                import_log.failed_imports,
            )

    except Exception as e:  # noqa
        logging.error("An error occurred while handling failed import:", exc_info=True)


@transaction.atomic
def handle_import_log_status(import_log, successful_imports, failed_imports):
    """
    Обработка статуса журнала импорта.

    Args:
        import_log: Экземпляр журнала импорта.
        successful_imports (int): Количество успешных импортов.
        failed_imports (int): Количество неудачных импортов.
    """
    if failed_imports > 0:
        import_log.status = "Завершён с ошибкой"
    else:
        import_log.status = "Выполнен"

    import_log.total_products = successful_imports + failed_imports
    import_log.successful_imports = successful_imports
    import_log.failed_imports = failed_imports
    import_log.save()


def handle_destination_path(content, import_log, successful_imports_dir, failed_imports_dir):
    """
    Обработка пути назначения для успешного и неудачного импорта.

    Args:
        file_name (str): Название импортированного файла.
        content (str): Содержимое файла.
        import_log: Экземпляр журнала импорта.
        successful_imports_dir (str): Директория для успешных импортов.
        failed_imports_dir (str): Директория для неудачных импортов.
    """
    os.makedirs(failed_imports_dir, exist_ok=True)

    new_file_name = f"{import_log.timestamp.strftime('%H-%M-%S_%d-%m-%Y')}_{get_shop_name(import_log.user.id)}.csv"

    destination_dir = successful_imports_dir if import_log.failed_imports == 0 else failed_imports_dir
    destination_path = os.path.join(destination_dir, new_file_name)

    with open(destination_path, "w", encoding="utf-8") as dest_file:
        dest_file.write(content)

    if import_log.failed_imports == 0:
        notify_admin_about_import_success(
            import_log.user.id,
            new_file_name,
            import_log.total_products,
            import_log.successful_imports,
            import_log.failed_imports,
        )


def extract_data_from_row(row: List[str]) -> Optional[Tuple[str, str, str, str, dict, List[str], str, str]]:
    """
    Извлекает данные из строки CSV и возвращает кортеж с данными продукта.

    :param row: Строка CSV.
    :return: Кортеж с данными продукта или None, если строка содержит заголовок.
    """
    try:
        if row[0].lower() == "name":
            return None

        name = row[0].strip()
        main_category_name = row[1].strip()
        subcategory_name = row[2].strip()
        description = row[3].strip()
        details = row[4::2]
        values = row[5::2]
        tags = [tag.strip() for tag in row[10].split(",")] if row[10] else []
        price = row[11].strip()
        remains = row[12].strip()

        details_dict = {}

        for detail, value in zip(details, values):
            details_dict[detail.strip()] = value.strip()

        return name, main_category_name, subcategory_name, description, details_dict, tags, price, remains
    except IndexError:
        return None


@transaction.atomic
def process_import_common(uploaded_file, user_id: int) -> str:  # noqa: C901
    """
    Обрабатывает общий процесс импорта.

    Args:
        uploaded_file: Загруженный файл.
        user_id: Идентификатор пользователя.

    Returns:
        str: Сообщение об ошибке, если есть, в противном случае пустая строка.
    """
    try:
        acquire_lock()
        file_name = uploaded_file.name
        content = uploaded_file.read().decode("utf-8")

        if not content.strip():
            return handle_empty_file(file_name, user_id)

        lines = content.split("\n")
        csv_rows = reader(lines)
        total_products, successful_imports, failed_imports = 0, 0, 0

        user = User.objects.get(id=user_id)
        import_log = get_existing_in_progress_import_log(user, file_name)

        if import_log is None:
            import_log = create_import_log(file_name, user, "in_progress")
        else:
            import_log.status = "in_progress"
            import_log.total_products = 0
            import_log.successful_imports = 0
            import_log.failed_imports = 0
            import_log.error_details = None
            import_log.save()

        site_settings = SiteSettings.load()
        successful_imports_dir = os.path.join(site_settings.docs_dir, site_settings.successful_imports_dir)
        failed_imports_dir = os.path.join(site_settings.docs_dir, site_settings.failed_imports_dir)

        for row in csv_rows:
            try:
                product_data = extract_data_from_row(row)
                if product_data is None:
                    continue
                create_product_and_offer(product_data, import_log, user_id)
                total_products += 1
                successful_imports += 1

            except (IndexError, Exception) as e:
                handle_failed_import(e, file_name, user_id, total_products, successful_imports, failed_imports)
                failed_imports += 1

        if total_products == 0 or failed_imports > 0:
            import_log.status = "Завершён с ошибкой"
            log_and_notify_error(
                "Import process failed", user_id, file_name, total_products, successful_imports, failed_imports
            )
            destination_dir = failed_imports_dir
        else:
            import_log.status = "Выполнен"
            destination_dir = successful_imports_dir

        import_log.total_products = total_products
        import_log.successful_imports = successful_imports
        import_log.failed_imports = failed_imports
        import_log.save()

        os.makedirs(destination_dir, exist_ok=True)
        new_file_name = f"{import_log.timestamp.strftime('%H-%M-%S_%d-%m-%Y')}_{get_shop_name(import_log.user.id)}.csv"
        destination_path = os.path.join(destination_dir, new_file_name)
        with open(destination_path, "w", encoding="utf-8") as dest_file:
            dest_file.write(content)
        if total_products > 0 and failed_imports == 0:
            notify_admin_about_import_success(
                user_id,
                new_file_name,
                total_products,
                successful_imports,
                failed_imports,
            )

    except (IntegrityError, ImportError, Exception) as e:
        error_message = _("Произошла ошибка: {e}").format(error=str(e))
        handle_failed_import(e, file_name, user_id, total_products, successful_imports, failed_imports)
        return error_message
    finally:
        release_lock()

    return ""
