"""Функции для кэширования данных о товаре и сервисы приложения products"""
from decimal import Decimal
from typing import Optional
from django.core.cache import cache

from products.models import Product


def gen_cache_key(product_id: int) -> str:
    """Возвращает ключ для кэширования"""

    return f"product_details_{product_id}"


def cache_product_details(product_id: int, expiration_time: int = 86400) -> Product:
    """
    Кэшировать детали продукта и установить опциональное время истечения срока действия.

    Параметры:
    - product_id: Идентификатор продукта для кэширования
    - expiration_time: Время истечения срока действия в секундах (по умолчанию 24 часа)
    """
    cache_key = gen_cache_key(product_id)
    product = fetch_product_details_from_database(product_id)

    cache.set(cache_key, product, expiration_time)
    return product


def invalidate_product_details_cache(product_id: int) -> None:
    """
    Сбросить кэш для деталей продукта.

    Параметры:
    - product_id: Идентификатор продукта для сброса кэша
    """
    cache_key = gen_cache_key(product_id)
    cache.delete(cache_key)


def fetch_product_details_from_database(product_id: int) -> Optional[Product]:
    """
    Замените эту функцию фактической логикой получения деталей продукта из базы данных.

    Параметры:
    - product_id: Идентификатор продукта

    Возвращает:
    - Детали продукта из базы данных
    """
    try:
        product = Product.objects.get(id=product_id)
        return product
    except Product.DoesNotExist:
        return None


def get_from_cache_or_set(product_id: int) -> Optional[Product]:
    """Возвращает детали продукта из кэша, либо из бд, сохранив в кэше"""

    cache_key = gen_cache_key(product_id)
    product = cache.get(cache_key)
    if product:
        return product
    return cache_product_details(product_id)


def get_discount_for_product(product: Product) -> Decimal:
    """Возвращает процент скидки на товар"""

    discount = product.discount_products.order_by("-percentage").first()
    if discount:
        return Decimal(1 - discount.percentage / 100)
    return Decimal("1")
