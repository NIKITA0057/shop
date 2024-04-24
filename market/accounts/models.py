"""Django-модели, представляющие пользователей интернет-магазина."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from products.models import Product


class User(AbstractUser):
    """Модель пользователя"""

    username = models.CharField(unique=False, blank=True, verbose_name=_("Имя пользователя"))
    USERNAME_FIELD = "email"
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    REQUIRED_FIELDS = []

    class Meta:
        """
        Метаданные модели "Пользователь"
        """

        app_label = "accounts"
        verbose_name = _("пользователь")
        verbose_name_plural = _("пользователи")


class ViewHistory(models.Model):
    """Модель истории просмотра товаров пользователем"""

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_("пользователь"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("товар"))
    view_date = models.DateTimeField(auto_now_add=True, verbose_name=_("дата просмотра"))
    view_count = models.IntegerField(default=0, verbose_name=_("количество просмотров"))

    class Meta:
        """Метаданные модели "История просмотров" """

        verbose_name = _("история просмотров")
        verbose_name_plural = _("истории просмотров")

    def __str__(self):
        return f"{self.user} - {self.product} - {self.view_date}"
