""" Модуль с фильтрами приложения products """

import django_filters
from django.db.models import QuerySet, Count, Sum
from django_filters import CharFilter
from django_filters.filters import ModelMultipleChoiceFilter, ModelChoiceFilter
from django.utils.translation import gettext_lazy as _
from products.models import Tag, Category, Product
from shops.models import Offer


class CustomOrderingFilter(django_filters.OrderingFilter):
    """Для добавления сортировки по полю, отсутствующему в модели"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra["choices"] += [
            ("popularity", _("Популярности")),
            ("-popularity", _("Популярности (по убыванию)")),
            ("reviews", _("Отзывам")),
            ("-reviews", _("Отзывам (по убыванию)")),
        ]

    def filter(self, qs, value):
        if value and any(v in ["popularity", "-popularity"] for v in value):
            qs = qs.annotate(cnt=Sum("offer__remains"))
            if "popularity" in value:
                return qs.order_by("-cnt")
            return qs.order_by("cnt")

        if value and any(v in ["reviews", "-reviews"] for v in value):
            qs = qs.annotate(cnt=Count("reviews__id"))
            if "reviews" in value:
                return qs.order_by("-cnt")
            return qs.order_by("cnt")

        return super().filter(qs, value)


class ProductFilter(django_filters.FilterSet):
    """Фильтр для сортировки товаров в каталоге"""

    name = CharFilter(field_name="name", lookup_expr="icontains")

    price_range = CharFilter(
        method="filter_price_range",
        help_text="Фильтр по диапазону цен товаров",
    )
    category = ModelChoiceFilter(field_name="category__name", to_field_name="name", queryset=Category.objects.all())

    tag = ModelMultipleChoiceFilter(
        field_name="tags__name",
        to_field_name="name",
        queryset=Tag.objects.all(),
    )

    is_exist = CharFilter(method="filter_exist")

    o = CustomOrderingFilter(
        # tuple-mapping retains order
        fields=(
            ("avg_price", "avg_price"),
            ("created_at", "created_at"),
        ),
        field_labels={"avg_price": _("Цене"), "created_at": _("Новизне")},
    )

    class Meta:
        """Метаданные класса ProductFilter"""

        model = Product
        fields = {"name": ["iexact", "icontains"]}

    def filter_price_range(self, queryset: QuerySet[Offer], _: str, value: str) -> QuerySet[Offer]:
        """Фильтрация по максимальной средней цене товара."""
        price_min, price_max = value.split(";")
        return queryset.filter(avg_price__gte=price_min).filter(avg_price__lte=price_max)

    def filter_exist(self, queryset, name, value):
        """Фильтрация товаров по наличию"""
        if value:
            return queryset.filter(remains__gt=0)
        return queryset

    def get_ordering_fields(self) -> list[tuple[str, str]]:
        """Возвращает параметры сортировки и их название для отображения на странице"""

        return [item for item in list(self.filters["o"].field.choices)[1:] if not item[0].startswith("-")]
