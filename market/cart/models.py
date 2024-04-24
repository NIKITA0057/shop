"""Модели приложения cart"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from shops.models import Offer


class Cart(models.Model):
    """Модель корзины"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts", verbose_name=_("пользователь"))
    is_active = models.BooleanField(default=True, verbose_name=_("активный"))

    class Meta:
        """Метаданные класса Cart"""

        verbose_name = _("корзина")
        verbose_name_plural = _("корзины")

    def __str__(self):
        return f"Cart {self.user}"


class ProductInCart(models.Model):
    """Модель товара в корзине"""

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, verbose_name=_("предложения"))
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="offers", verbose_name=_("корзина"))
    quantity = models.PositiveIntegerField(verbose_name=_("количества"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("дата создания"))

    class Meta:
        """Метаданные класса ProductInCart"""

        verbose_name = _("товар в корзине")
        verbose_name_plural = _("товары в корзине")
        ordering = ("-created_at",)

    def __str__(self):
        return f"Product {self.offer.product} in cart {self.cart}"
