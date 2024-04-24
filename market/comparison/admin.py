"""Настройки админ панели приложения Comparison"""
from django.contrib import admin  # noqa F401
from .models import Comparison


admin.site.register(Comparison)
