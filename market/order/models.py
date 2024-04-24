"""
Модуль, содержащий модели для управления заказами в приложении.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from cart.models import Cart


class PaymentTypes(models.TextChoices):
    """
    Типы оплаты для заказов.
    """

    CARD = "card", "Онлайн картой"


class OrderStatus(models.TextChoices):
    """
    Статусы заказов.
    """

    CREATED = "created", "Создан"
    PAID = "paid", "Оплачен"
    NOT_PAID = "not_paid", "Не оплачен"


class DeliveryTypes(models.TextChoices):
    """
    Типы доставки для заказов.
    """

    REGULAR = "regular", "Обычная доставка"
    EXPRESS = "express", "Экспресс-доставка"


class Order(models.Model):
    """Модель заказа"""

    name = models.TextField(max_length=20, blank=False, null=False, verbose_name=_("имя"))
    phone = models.IntegerField(verbose_name=_("телефон"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("пользователь"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("дата создания"))
    delivery_type = models.CharField(
        max_length=50,
        choices=DeliveryTypes.choices,
        verbose_name="delivery type",
        blank=False,
        default=DeliveryTypes.REGULAR,
    )
    city = models.CharField(max_length=50, verbose_name=_("город"))
    address = models.CharField(max_length=255, verbose_name=_("адрес"))
    payment_type = models.CharField(
        max_length=50,
        choices=PaymentTypes.choices,
        blank=False,
        default=PaymentTypes.CARD,
        verbose_name=_("Способ оплаты"),
    )
    status = models.CharField(
        max_length=15, choices=OrderStatus.choices, default=OrderStatus.CREATED, verbose_name=_("статус")
    )
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, verbose_name=_("корзина"))
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Общая стоимость"))

    class Meta:
        """Определение мета-атрибутов модели заказа."""

        db_table = "order"
        verbose_name = _("заказ")
        verbose_name_plural = _("заказы")
