"""Настройки админки приложения cart"""

from django.contrib import admin  # noqa F401
from .models import ProductInCart, Cart

admin.site.register(Cart)
admin.site.register(ProductInCart)
