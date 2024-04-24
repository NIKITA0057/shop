""" Сервисы главной страницы """
import datetime
import random
from typing import Any

from django.core.cache import cache
from django.db.models import QuerySet, Count, Min, Sum, Avg

from products.models import Product, Banner, Category
from settings_app.models import SiteSettings
from shops.models import Offer


class MainPageService:
    """Сервисы главной страницы"""

    def get_cache_key(self, prefix) -> str:
        """Генерация ключа кэша"""
        return f"{prefix}_main_page"

    def get_top_products(self) -> QuerySet:
        """Самые продаваемые продукты"""
        cache_key = self.get_cache_key("top_products")
        result = cache.get(cache_key)
        if result is None:
            result = Offer.objects.order_by("remains").select_related("product")[:8]
            cache.set(cache_key, result)

        return result

    def get_top_categories(self) -> list[Any]:
        """Самые популярные категории"""
        cache_key = self.get_cache_key("top_categories")
        result = cache.get(cache_key)
        if result is None:
            categories = (
                Category.objects.all()
                .annotate(cnt=Count("category"))
                .annotate(min_price=Min("product__offer__price"))
                .annotate(remains=Sum("product__offer__remains"))
                .filter(cnt=0)
                .order_by("remains")
            )
            result = [category for category in categories if category.is_active()][:3]
            cache.set(cache_key, result)

        return result

    def get_hot_offers(self) -> QuerySet:
        """Горячие предложения"""

        cache_key = self.get_cache_key("hot_offers")
        result = cache.get(cache_key)
        if result is None:
            products = (
                Product.objects.all()
                .annotate(cnt=Count("discount_products"))
                .annotate(avg_price=Avg("offer__price"))
                .filter(cnt__gt=0)
            )
            result = random.sample(list(products), k=9)
            cache.set(cache_key, result)
        return result

    def get_limited_products(self) -> QuerySet:
        """Ограниченные предложения"""
        cache_key = self.get_cache_key("limited_products")
        result = cache.get(cache_key)
        if result is None:
            result = (
                Product.objects.annotate(avg_price=Avg("offer__price"))
                .filter(is_limited=True)
                .filter(is_product_of_the_day=False)
            )[:16]

            cache.set(cache_key, result)
        return result

    def get_product_of_day(self) -> Product:
        """Товар дня"""

        return Product.objects.annotate(avg_price=Avg("offer__price")).filter(is_product_of_the_day=True).first()

    def get_tomorrow_date(self) -> datetime:
        """Возвращает объект времени полночи следующего дня"""
        today = datetime.datetime.today()
        one_day = datetime.timedelta(days=1)
        return today + one_day

    def banners_cache(self) -> QuerySet:
        """
        Функция возвращает 3 случайных объекта модели Banner в кэшированном виде.
        """

        cache_key = "banners_cache"
        data = cache.get(cache_key)
        banners_expiration_time = SiteSettings.load().banners_expiration_time
        if not data:
            data = Banner.objects.filter(actual=True).order_by("?")[:3]
            cache.set(cache_key, data, banners_expiration_time)
        return data
