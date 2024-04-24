# Generated by Django 4.2.11 on 2024-04-15 11:44

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import shops.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("products", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Offer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("price", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="цена")),
                ("remains", models.IntegerField(default=0, verbose_name="осталось")),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="products.product", verbose_name="продукт"
                    ),
                ),
            ],
            options={
                "verbose_name": "предложения",
                "verbose_name_plural": "предложение",
            },
        ),
        migrations.CreateModel(
            name="Shop",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(blank=True, max_length=512, null=True, verbose_name="название")),
                (
                    "contact_info",
                    models.CharField(blank=True, max_length=512, null=True, verbose_name="контактная информация"),
                ),
                ("description", models.TextField(blank=True, null=True, verbose_name="описание")),
                (
                    "logo",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=shops.models.shop_logo_directory_path,
                        validators=[
                            django.core.validators.FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])
                        ],
                        verbose_name="логотип компании",
                    ),
                ),
                (
                    "products",
                    models.ManyToManyField(
                        related_name="shops",
                        through="shops.Offer",
                        to="products.product",
                        verbose_name="товары в магазине",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "продавец",
                "verbose_name_plural": "продавцы",
            },
        ),
        migrations.AddField(
            model_name="offer",
            name="shop",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="shops.shop", verbose_name="магазин"
            ),
        ),
        migrations.AddConstraint(
            model_name="offer",
            constraint=models.UniqueConstraint(models.F("shop"), models.F("product"), name="unique_product_in_shop"),
        ),
    ]