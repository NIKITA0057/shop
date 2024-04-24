# pylint: disable=C0103
""" Модуль для определения URL-путей приложения настройки settings_app """
from django.urls import path

from .views import ResetCacheView, SettingsView

app_name = "settings_app"

urlpatterns = [
    path("reset-cache/", ResetCacheView.as_view(), name="reset_cache"),
    path("sitesettings/add/", SettingsView.as_view(), name="sitesettings_add"),
    path("sitesettings/<int:pk>/change/", SettingsView.as_view(), name="sitesettings_change"),
]
