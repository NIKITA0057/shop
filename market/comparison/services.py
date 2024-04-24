"""
Модуль для работы со сравнением продуктов.

Этот модуль содержит функции и классы для управления сравнением продуктов,
включая добавление и удаление продуктов из сравнения, получение списка
продуктов в сравнении и проверку общих характеристик среди продуктов.

"""
import logging

from comparison.models import Comparison
from products.models import Product

logger = logging.getLogger(__name__)

MAX_PRODUCTS_FOR_COMPARISON = 4


def add_to_comparison_service(user, product_id):
    """
     Добавляет продукт в сравнение для пользователя.

    :param user: Идентификатор пользователя.
    :param product_id: Идентификатор продукта.
    :return: Кортеж (успешно добавлено, создано новое сравнение).
    """
    comparison, created = Comparison.objects.get_or_create(user=user)

    if created:
        logger.info("Comparison created for user %s", user)

    if comparison.products.count() < MAX_PRODUCTS_FOR_COMPARISON:
        if product_id not in comparison.products.values_list("id", flat=True):
            product = Product.objects.filter(id=product_id).first()
            if product:
                comparison.products.add(product)
                logger.info("Product %s added to comparison for user %s", product, user)
                return True, created
    else:
        logger.warning(
            "Failed to add product %s to comparison for user %s. Maximum number of products reached.", product_id, user
        )

    return False, created


def remove_from_comparison(user, product_id):
    """
    Удаляет продукт из сравнения для пользователя.

    :param user: Идентификатор пользователя.
    :param product_id: Идентификатор продукта.
    :return: True, если успешно удалено, в противном случае False.
    """
    comparison, created = Comparison.objects.get_or_create(user=user)

    try:
        product = Product.objects.get(pk=product_id)
        comparison.products.remove(product)

        return True
    except Product.DoesNotExist:
        logger.error("Product with ID %s not found for user %s", product_id, user)
        return False


def get_comparison_list(user_id):
    """
    Получает список продуктов в сравнении для пользователя.

    :param user_id: Идентификатор пользователя.
    :return: Список продуктов в сравнении.
    """
    try:
        comparison = Comparison.objects.get(user_id=user_id)
        return comparison.products.all()
    except Comparison.DoesNotExist:
        logger.warning("No comparison found for user %s", user_id)
        return []


def get_products_for_comparison(product_ids):
    """
     Получает продукты из базы данных на основе предоставленных идентификаторов продуктов.

    :param product_ids: Список идентификаторов продуктов.
    :return: Список продуктов.
    """
    return Product.objects.filter(id__in=product_ids)


def check_common_details(products):
    """
    Проверяет, есть ли общие характеристики среди продуктов.

    :param products: Список продуктов.
    :return: Словарь общих характеристик, если они есть, в противном случае None.
    """
    if not products:
        return None

    first_product_details = products[0].details

    common_details = {}

    for key, value in first_product_details.items():
        common = True
        for product in products[1:]:
            if key not in product.details:
                common = False
                break
        if common:
            common_details[key] = value

    return common_details if common_details else None


class ComparisonService:
    """Сервис для управления сравнениями продуктов."""

    def __init__(self):
        self.comparison_model = Comparison
