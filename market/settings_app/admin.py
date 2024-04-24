"""
Модуль, содержащий пользовательский администратор модели настроек сайта.

Этот модуль определяет административный интерфейс для модели настроек сайта
и добавляет пользовательские URL-адреса для создания и изменения настроек сайта.
"""
from typing import List

from django.contrib import admin
from django.urls import path

from .forms import SiteSettingsForm
from .models import SiteSettings
from .views import SettingsView


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """
    Пользовательский администратор модели настроек сайта.

    Этот класс определяет административный интерфейс для модели настроек сайта
    и добавляет пользовательские URL-адреса для создания и изменения настроек сайта.
    """

    form: SiteSettingsForm  # Форма, используемая для создания и редактирования настроек сайта

    change_form_template: str = "settings_app/settings.html"  # Шаблон для редактирования настроек

    def get_urls(self) -> List[path]:
        """
        Получает URL-адреса администратора для модели настроек сайта.

        Возвращает список пользовательских URL-адресов для создания и изменения настроек сайта,
        а также стандартные URL-адреса администратора.
        """
        urls: List[path] = super().get_urls()
        custom_urls: List[path] = [
            path("sitesettings/add/", self.admin_site.admin_view(SettingsView.as_view()), name="sitesettings_add"),
            path(
                "sitesettings/<int:pk>/change/",
                self.admin_site.admin_view(SettingsView.as_view()),
                name="sitesettings_change",
            ),
        ]
        return custom_urls + urls
