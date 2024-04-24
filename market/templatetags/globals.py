"""Модуль глобальных функций django_jinja"""

from django_jinja import library

from products.models import Category


@library.global_function
def get_categories() -> dict:
    """Получение всех категорий"""
    all_categories = Category.objects.select_related("parent")

    children = {}

    for category in all_categories:
        children[category.id] = category.category_set.all()

    return {
        "main_categories": all_categories.filter(parent=None),
        "children": children,
    }
