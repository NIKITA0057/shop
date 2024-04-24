"""Django-модели приложения shops"""
import os

from django.conf import settings

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User


def shop_logo_directory_path(instance: "Shop", filename: str) -> str:
    """Функция, гененрирующая путь, по которому будет храниться логотип компании-продавца"""
    return os.path.join(settings.MEDIA_ROOT, f"shops/shop_{instance.name}/{filename}")


class Shop(models.Model):
    """Модель магазина, который является продавцом на маркетплейсе Megano"""

    name = models.CharField(max_length=512, verbose_name=_("название"), blank=True, null=True)
    contact_info = models.CharField(max_length=512, verbose_name=_("контактная информация"), blank=True, null=True)
    description = models.TextField(verbose_name=_("описание"), blank=True, null=True)
    products = models.ManyToManyField(
        "products.Product",
        through="Offer",
        related_name="shops",
        verbose_name=_("товары в магазине"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("пользователь"))
    logo = models.ImageField(
        upload_to=shop_logo_directory_path,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])],
        verbose_name=_("логотип компании"),
        blank=True,
        null=True,
    )

    class Meta:
        """Метаинформация о модели 'Магазин'."""

        verbose_name = _("продавец")
        verbose_name_plural = _("продавцы")

    def __str__(self):
        return f"{self.name}"


class Offer(models.Model):
    """Предложение магазина"""

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name=_("магазин"))
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, verbose_name=_("продукт"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("цена"))
    remains = models.IntegerField(default=0, verbose_name=_("осталось"))

    class Meta:
        """Метаинформация о модели 'Предложение'."""

        constraints = [models.UniqueConstraint("shop", "product", name="unique_product_in_shop")]
        verbose_name = _("предложения")
        verbose_name_plural = _("предложение")
