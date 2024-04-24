"""Модуль, содержащий форму для магазина."""
from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Shop


class ShopForm(forms.ModelForm):
    """Форма для создания и редактирования магазинов."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Инициализация формы.

        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        """
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != "logo":
                field.required = True

    class Meta:
        """Метаинформация о форме."""

        model = Shop
        fields = ["name", "contact_info", "description", "logo"]
        labels = {
            "name": _("Название магазина"),
            "contact_info": _("Контактная информация"),
            "description": _("Описание"),
            "logo": _("Логотип"),
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Введите название магазина")}),
            "contact_info": forms.TextInput(
                attrs={"class": "form-control", "placeholder": _("Введите контактную информацию")}
            ),
            "description": forms.Textarea(attrs={"class": "form-control", "placeholder": _("Введите описание")}),
            "logo": forms.ClearableFileInput(attrs={"class": "form-control-file", "placeholder": _("Выберите файл")}),
        }

    def clean_contact_info(self) -> str:
        """
        Очистка данных контактной информации.

        :return: Очищенная контактная информация.
        """
        contact_info: str = self.cleaned_data["contact_info"]
        return contact_info
