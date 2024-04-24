""" Формы приложения Cart """

from django import forms


class CartAddProductForm(forms.Form):
    """Форма для обновления количества товаров в корзине"""

    quantity = forms.IntegerField(
        min_value=1,
        max_value=21,
        widget=forms.TextInput(
            attrs={
                "class": "Amount-input form-input",
                "readonly": True,
            }
        ),
        label="",
    )
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
