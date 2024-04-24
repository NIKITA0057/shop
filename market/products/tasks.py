"""Периодические задачи celery"""
import random

from celery import shared_task

from products.models import Product


@shared_task(name="Установить товар дня")
def set_product_of_the_day():
    """Рандомный выбор товара дня"""
    current_product_of_the_day = Product.objects.filter(is_product_of_the_day=True).first()
    products = Product.objects.filter(is_limited=True).filter(is_product_of_the_day=False)
    if products.exists():
        new_product_of_the_day = random.choice(products)
        new_product_of_the_day.is_product_of_the_day = True
        new_product_of_the_day.save()
        if current_product_of_the_day is not None:
            current_product_of_the_day.is_product_of_the_day = False
            current_product_of_the_day.save()
