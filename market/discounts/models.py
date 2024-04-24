"""Модели приложения discounts"""
from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from products.models import Product


class DiscountBase(models.Model):
    """Базовая модель скидок"""

    title = models.CharField(max_length=100, verbose_name=_("название акции"))
    description = models.TextField(verbose_name=_("описание акции"))
    start_date = models.DateField(verbose_name=_("начало акции"))
    end_date = models.DateField(verbose_name=_("окончание акции"))
    is_active = models.BooleanField(default=True, verbose_name=_("статус активности скидки"))
    weight = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        verbose_name=_("вес скидки"),
        validators=[MinValueValidator(0.01), MaxValueValidator(1.00)],
    )

    class Meta:
        """Метаданные класса DiscountBase"""

        abstract = True

    def is_relevant(self):
        """Проверяет актуальность скидки"""
        now = timezone.now().date()
        return self.start_date <= now <= self.end_date


class DiscountPercentageBase(DiscountBase):
    """Базовая модель для скидок с процентом"""

    percentage = models.PositiveIntegerField(default=0, verbose_name=_("процент скидки"))

    class Meta:
        """Метаданные класса DiscountPercentageBase"""

        abstract = True

    def save(self, *args, **kwargs):
        self.percentage = min(self.percentage, 99)
        self.percentage = max(self.percentage, 1)

        super(DiscountBase, self).save(*args, **kwargs)

    def __str__(self):
        return f"{_('процент')}={self.percentage}%, {_('событие')}: {self.title}"


class DiscountProduct(DiscountPercentageBase):
    """Модель для хранения скидок на товары"""

    products = models.ManyToManyField(Product, related_name="discount_products", verbose_name=_("продукты"))

    class Meta:
        """Метаданные класса DiscountProduct"""

        verbose_name = _("скидка на товар")
        verbose_name_plural = _("скидки на товары")
        ordering = ["-weight"]


class DiscountSet(DiscountBase):
    """Модель для хранения скидок на наборы товаров"""

    first_group = models.ManyToManyField(Product, related_name="first_group", verbose_name=_("первая группа"))
    second_group = models.ManyToManyField(Product, related_name="second_group", verbose_name=_("вторая группа"))
    discount_amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name=_("размер скидки"),
        validators=[MinValueValidator(1.0)],
    )

    class Meta:
        """Метаданные класса DiscountSet"""

        verbose_name = _("скидка на набор товаров")
        verbose_name_plural = _("скидки на наборы товаров")

    def __str__(self):
        return f"{_('размер скидки')}={self.discount_amount}, {_('событие')}: {self.title}"


class DiscountCart(DiscountPercentageBase):
    """Модель для хранения скидок на стоимость корзины"""

    price_from = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("диапазон цены от"))
    price_to = models.DecimalField(
        default=Decimal("Infinity"), max_digits=10, decimal_places=2, verbose_name=_("диапазон цены до")
    )

    class Meta:
        """Метаданные класса DiscountCart"""

        verbose_name = _("скидка на стоимость корзины")
        verbose_name_plural = _("скидки на стоимость корзины")
