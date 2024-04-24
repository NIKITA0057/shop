# pylint: disable=R0901
"""Представления приложения discounts"""

from django.views.generic import ListView, DetailView

from discounts.models import DiscountProduct, DiscountCart, DiscountSet


class DiscountListView(ListView):
    """Страница с отображением всех скидок"""

    template_name = "discounts/discounts_list.jinja2"
    model = DiscountProduct
    context_object_name = "discounts"
    ordering = "end_date"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        discount_set = (
            DiscountSet.objects.prefetch_related("first_group", "second_group")
            .order_by("end_date")
            .filter(is_active=True)
        )
        discount_carts = DiscountCart.objects.all().order_by("end_date").filter(is_active=True)

        context["discount_sets"] = discount_set
        context["discount_carts"] = discount_carts
        return context

    def get_queryset(self):
        return DiscountProduct.objects.prefetch_related("products").filter(is_active=True)


class DiscountProductDetailView(DetailView):
    """Детальная страница скидки продукта"""

    template_name = "discounts/discount-product.jinja2"
    model = DiscountProduct
    context_object_name = "discount_product"


class DiscountCartDetailView(DetailView):
    """Детальная страница скидки корзины"""

    template_name = "discounts/discount-cart.jinja2"
    model = DiscountCart
    context_object_name = "discount_cart"


class DiscountSetDetailView(DetailView):
    """Детальная страница скидки категории"""

    template_name = "discounts/discount-set.jinja2"
    model = DiscountSet
    context_object_name = "discount_set"
