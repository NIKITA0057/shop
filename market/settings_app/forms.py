"""
Модуль, содержащий форму для создания и редактирования настроек сайта.

Этот модуль предоставляет форму `SiteSettingsForm`, которая используется
для создания и изменения настроек сайта, используя соответствующую модель `SiteSettings`.
"""
from typing import Type

from django import forms

from .models import SiteSettings


class SiteSettingsForm(forms.ModelForm):
    """
    Форма для создания и редактирования настроек сайта.

    Эта форма позволяет пользователю создавать и изменять настройки сайта,
    используя соответствующую модель `SiteSettings`.
    """

    class Meta:
        """Метакласс, определяющий свойства формы."""

        model: Type[SiteSettings] = SiteSettings  # Модель, связанная с формой
        fields: list[str] = [
            "docs_dir",
            "fixture_dir",
            "successful_imports_dir",
            "failed_imports_dir",
            "banners_expiration_time",
            "email_access_settings",
            "paginate_products_by",
        ]  # Поля, отображаемые в форме для редактирования настроек сайта
