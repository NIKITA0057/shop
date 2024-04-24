"""Настройки админ панели приложения discounts"""

from django.contrib import admin
from .models import DiscountProduct, DiscountSet, DiscountCart


class DiscountSetAdmin(admin.ModelAdmin):
    """Класс с настройками модели скидок на наборы при отображении на админ панели"""

    list_display = ["title", "description", "discount_amount", "start_date", "end_date"]


class DiscountCartAdmin(admin.ModelAdmin):
    """Класс с настройками модели скидок на корзину при отображении на админ панели"""

    list_display = ["title", "description", "percentage", "start_date", "end_date", "price_from", "price_to"]


class DiscountProductAdmin(admin.ModelAdmin):
    """Класс с настройками модели скидок на продукты при отображении на админ панели"""

    list_display = ["title", "description", "percentage", "start_date", "end_date", "is_active"]


admin.site.register(DiscountProduct, DiscountProductAdmin)
admin.site.register(DiscountSet, DiscountSetAdmin)
admin.site.register(DiscountCart, DiscountCartAdmin)
