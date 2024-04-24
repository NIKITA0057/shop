""" Сервисы страницы каталога товаров """
from typing import Tuple

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import ProgrammingError
from django.db.models import Count
from django.http import HttpRequest

from products.models import Tag
from settings_app.models import SiteSettings
from settings_app.singleton_model import PAGINATE_PRODUCTS_BY


def get_popular_tags() -> list:
    """Возвращает популярные теги"""

    return Tag.objects.all().annotate(cnt=Count("product")).order_by("-cnt")[:5]


def get_full_path_of_request_without_param_page(request: HttpRequest) -> Tuple[str, bool]:
    """Возвращает полый url запроса"""
    url = request.get_full_path()
    return relative_url(url)


def relative_url(url: str) -> Tuple[str, bool]:
    """Создание url для отображения страниц пагинации с фильтрацией"""
    if "?" not in url:
        return url, False
    if "page" not in url:
        return url, True
    params = url.split("?")[1].split("&")
    params = [param for param in params if not param.startswith("page")]
    return url.split("?")[0] + "?" + "&".join(params), True


def get_paginate_products_by() -> int:
    """Возвращает значение поля paginate_products_by если доступно, иначе значение по умолчанию"""
    try:
        res = SiteSettings.load().paginate_products_by
        if not res:
            res = PAGINATE_PRODUCTS_BY
    except (ProgrammingError, ObjectDoesNotExist):
        res = PAGINATE_PRODUCTS_BY
    return res
