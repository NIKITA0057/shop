"""Django-модель, представляющая продукт."""

from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _


class Banner(models.Model):
    """Баннер"""

    name = models.CharField(max_length=512, verbose_name=_("названия"))
    description = models.TextField(verbose_name=_("описания"), null=True)
    actual = models.BooleanField(default=True, verbose_name=_("актуальность"))
    preview = models.ImageField(verbose_name=_("превью"), upload_to="banners")
    link = models.URLField(verbose_name=_("ссылка"), unique=True, db_index=True)

    class Meta:
        """Метаданные класса Banner"""

        verbose_name = _("Баннер")
        verbose_name_plural = _("Баннеры")
        app_label = "products"

    def __str__(self):
        return f"{self.name}"


class Category(models.Model):
    """Модель django orm категорий товара"""

    name = models.CharField(max_length=512, verbose_name=_("наименования"), unique=True)
    description = models.TextField(verbose_name=_("описания"), blank=True, null=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    sort_index = models.PositiveIntegerField(verbose_name=_("индекс сортировки"), null=True, unique=True)

    def is_active(self):
        """Проверяет, активна ли категория, имея ли хотя бы один продукт."""
        return self.product_set.exists()

    class Meta:
        """Метаданные класса Category"""

        verbose_name = _("категория")
        verbose_name_plural = _("категорий")

    def __str__(self):
        return f"{self.name}"


class Tag(models.Model):
    """Модель django orm тегов"""

    name = models.CharField(max_length=100, verbose_name=_("тег"), unique=True)

    class Meta:
        """Метаданные класса Tags"""

        verbose_name = _("тег")
        verbose_name_plural = _("теги")

    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    """Модель django orm товаров"""

    name = models.CharField(max_length=100, db_index=True, verbose_name=_("наименования"))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, max_length=100, verbose_name=_("категория"))
    description = models.CharField(max_length=1000, verbose_name=_("описания"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("дата создания"))
    details = models.JSONField(default=dict, blank=True, verbose_name=_("детали"))
    tags = models.ManyToManyField(Tag, related_name="product", verbose_name="тег")
    is_limited = models.BooleanField(default=False, verbose_name=_("ограниченный тираж"))
    is_product_of_the_day = models.BooleanField(default=False, verbose_name=_("товар дня"))

    class Meta:
        """Метаданные класса Product"""

        verbose_name = _("продукт")
        verbose_name_plural = _("продукты")

    def __str__(self):
        return f"{self.name}"


class Review(models.Model):
    """Модель отзыва на товар"""

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="reviews", verbose_name=_("пользователь")
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", verbose_name=_("продукт"))
    text = models.TextField(
        verbose_name=_("текст"),
        validators=[
            validators.MinLengthValidator(10),
            validators.MaxLengthValidator(1000),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("дата создания"))
    rating = models.IntegerField()

    class Meta:
        """Метаданные класса Review"""

        verbose_name = _("отзыв")
        verbose_name_plural = _("отзывы")
        unique_together = ("user", "product")

    def __str__(self):
        return f"Review for {self.product} by {self.user} from {self.created_at}"


class ProductImage(models.Model):
    """Модель фотографии товара"""

    image = models.ImageField(upload_to="products/%Y/%m/%d/", verbose_name=_("изображения"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images", verbose_name=_("продукт"))

    class Meta:
        """Метаданные класса ProductImage"""

        verbose_name = _("изображения")
        verbose_name_plural = _("изображение")

    def __str__(self):
        return f"{self.product.name}"
