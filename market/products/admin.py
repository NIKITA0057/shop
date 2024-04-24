"""Настройки админ панели приложения products"""
from django.contrib import admin  # noqa F401
from .models import Category, Product, Tag, ProductImage, Review

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Tag)
admin.site.register(ProductImage)
admin.site.register(Review)
