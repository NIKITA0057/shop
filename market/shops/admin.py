"""Настройки админ панели приложения shops"""
from django.contrib import admin  # noqa F401
from django.utils.safestring import mark_safe

from .models import Shop, Offer


class ShopAdmin(admin.ModelAdmin):
    """Администратор для модели 'Магазин'."""

    list_display = ("name", "contact_info", "description", "logo_display")
    list_filter = ("name", "user")
    search_fields = ("name", "contact_info", "description")

    def logo_display(self, obj):
        """Отображение текущего логотипа в админке."""
        if obj.logo:
            return mark_safe('<img src="{0}" width="100px" />'.format(obj.logo.url))
        else:
            return "No logo"

    logo_display.short_description = "Логотип"


admin.site.register(Shop, ShopAdmin)


class OfferAdmin(admin.ModelAdmin):
    """Администратор для модели 'Предложение'."""

    list_display = ("shop", "product", "price", "remains")
    list_filter = ("shop", "remains")
    search_fields = ("shop", "product")


admin.site.register(Offer, OfferAdmin)
