"""Сервисы приложения discounts"""

from typing import Tuple
from _decimal import Decimal

from django.utils import timezone

from shops.models import Offer
from .models import DiscountCart, DiscountProduct, DiscountSet


def calculate_set(offers: list[Offer]) -> Tuple[Decimal | int, int]:
    """Возвращает вес скидки и скидку на набор товаров"""

    discounts = DiscountSet.objects.filter(
        start_date__lte=timezone.now().date(), end_date__gte=timezone.now().date(), is_active=True
    ).order_by("-weight")

    weight = 0
    discount_amount = 0
    for discount in discounts:
        if any(offer.product in discount.first_group.all() for offer in offers) and any(
            offer.product in discount.second_group.all() for offer in offers
        ):
            return discount.weight, discount.discount_amount

    return weight, discount_amount


def calculate_cart(price: Decimal) -> Tuple[Decimal | int, int]:
    """Возвращает вес скидки и скидку на корзину"""

    discount_carts = DiscountCart.objects.filter(
        start_date__lte=timezone.now().date(), end_date__gte=timezone.now().date(), is_active=True
    ).order_by("-weight")

    weight = 0
    percentage = 0

    for discount in discount_carts:
        if discount.price_from <= price <= discount.price_to:
            weight = discount.weight
            percentage = discount.percentage
            return weight, percentage
    return weight, percentage


def calculate_product_price_with_discount(offer: Offer) -> Decimal:
    """Возвращает стоимость товара с учетом скидки"""

    discount_products = DiscountProduct.objects.filter(
        start_date__lte=timezone.now().date(), end_date__gte=timezone.now().date(), is_active=True
    ).order_by("-weight")

    price = offer.price

    for discount in discount_products:
        if offer.product in discount.products.all():
            return Decimal(price - price * discount.percentage / 100)
    return price
