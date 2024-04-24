"""
Модуль, содержащий формы для многоэтапной обработки заказов.

Эти формы предназначены для использования в процессе создания заказа
поэтапно, где каждая форма представляет собой отдельный этап процесса.

Классы:
    FirstStepForm: Форма для сбора имени и номера телефона.
    SecondStepForm: Форма для сбора города, адреса и типа доставки.
    ThirdStepForm: Форма для сбора типа оплаты.
"""

from django import forms
from .models import Order


class FirstStepForm(forms.ModelForm):
    """Форма для сбора имени и номера телефона."""

    class Meta:
        """Метаданные о форме"""

        model = Order
        fields = ("name", "phone")


class SecondStepForm(forms.ModelForm):
    """Форма для сбора информации о городе, адресе и типе доставки."""

    class Meta:
        """Метаданные о форме"""

        model = Order
        fields = ("city", "address", "delivery_type")


class ThirdStepForm(forms.ModelForm):
    """Форма для сбора информации о типах оплаты"""

    class Meta:
        """Метаданные о форме"""

        model = Order
        fields = ("payment_type",)
