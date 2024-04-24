"""
Модуль для настройки административного интерфейса Django.

Этот модуль содержит настройки административных интерфейсов для моделей `ImportLog` и `ImportLogProduct`.
"""

from django.contrib import admin

from .models import ImportLog, ImportLogProduct


@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    """
    Администрирование модели ImportLog.

    Attributes:
        list_display (tuple): Поля для отображения в списке записей.
        search_fields (tuple): Поля, по которым можно осуществлять поиск.
        list_filter (tuple): Поля для фильтрации списка записей.
        date_hierarchy (str): Имя поля для иерархии дат.
        ordering (tuple): Поля для сортировки списка записей.

    Methods:
        None
    """

    list_display = ("id", "user", "file_name", "status", "timestamp")
    search_fields = ("user__username", "file_name", "status")
    list_filter = ("status", "timestamp")
    date_hierarchy = "timestamp"
    ordering = ("-timestamp",)


@admin.register(ImportLogProduct)
class ImportLogProductAdmin(admin.ModelAdmin):
    """
    Администрирование модели ImportLogProduct.

    Attributes:
        list_display (tuple): Поля для отображения в списке записей.
        search_fields (tuple): Поля, по которым можно осуществлять поиск.
        list_filter (tuple): Поля для фильтрации списка записей.

    Methods:
        None
    """

    list_display = ("import_log", "product")
    search_fields = ("import_log__file_name", "product__name")
    list_filter = ("import_log__status",)
