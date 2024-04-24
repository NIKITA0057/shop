"""Представления приложения comparison"""
from typing import Union

from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.http import require_POST

from products.models import Product
from shops.models import Offer
from .services import (
    remove_from_comparison,
    add_to_comparison_service,
    get_comparison_list,
    get_products_for_comparison,
    check_common_details,
)


class ComparisonView(View):
    """
    Представление для страницы сравнения товаров.

    Позволяет пользователям просматривать и сравнивать товары.
    """

    def get(self, request) -> render:
        """Обработчик GET-запроса для страницы сравнения товаров."""
        comparison_list = get_comparison_list(request.user.id)
        comparison_count = len(comparison_list)
        products = get_products_for_comparison(comparison_list)
        common_details = check_common_details(products)

        context = {
            "products": products,
            "common_characteristics": common_details,
            "comparison_count": comparison_count,
        }

        if comparison_count < 2:
            no_enough_products = _("Недостаточно данных для сравнения")
            messages.error(request, no_enough_products)

        if not common_details:
            no_common_details = _(
                "Попытка сравнить товары без общих характеристик — "
                "как пытаться сравнить кота с карамельным поп-корном: "
                "нелепо и, в конечном итоге, только заставляет задуматься о бесполезности "
                "сравнения вещей, которые просто нельзя сравнить. Ведь каждый товар —"
                " это как своего рода экземпляр чуда, подобно тому, как каждый кот —"
                " это своя собственная тайна вселенной!"
            )
            messages.warning(
                request,
                no_common_details,
            )

        prices = {}
        for product in products:
            try:
                offer = Offer.objects.filter(product=product).order_by("price").first()
                prices[product.pk] = offer.price if offer else None
            except Offer.DoesNotExist:
                prices[product.pk] = None

        context["prices"] = prices

        return render(request, "comparison/comparison.jinja2", context)

    @staticmethod
    def comparison_count(request: HttpRequest) -> int:
        """Рассчитывает количество сравнений."""
        comparison_list = get_comparison_list(request.user.id)
        return len(comparison_list)

    @staticmethod
    def get_product_details(product_id: str) -> Union[str, None]:
        """Получает детали продукта по его идентификатору."""
        try:
            product: Product = Product.objects.get(pk=product_id)
            return product.details
        except Product.DoesNotExist:
            return None


@require_POST
def add_to_comparison(request, product_id: str) -> HttpResponseRedirect:
    """Обработчик POST-запроса для добавления товара в сравнение."""
    user = request.user if request.user.is_authenticated else None

    added: bool
    created: bool
    added, created = add_to_comparison_service(user, product_id)

    if added:
        if created:
            messages.success(request, _("Товар успешно добавлен в сравнение"))
        else:
            messages.info(request, _("Товар уже присутствует в сравнении"))
    else:
        max_products = _("Не удалось добавить товар в сравнение. Максимум 4 товара разрешены.")
        messages.error(request, max_products)

    return redirect("products:product-details", pk=product_id)


@require_POST
def remove_from_comparison_view(request) -> Union[HttpResponseRedirect, HttpResponse]:
    """Обработчик POST-запроса для удаления товара из сравнения."""

    user = request.user if request.user.is_authenticated else None
    if "product_id" in request.POST:
        product_id: str = request.POST["product_id"]
        success: bool = remove_from_comparison(user, product_id)
        if success:
            messages.success(request, _("Товар успешно удален из сравнения"))
        else:
            messages.error(request, _("Не удалось удалить товар из сравнения"))
    else:
        messages.error(request, _("Неверный запрос. Отсутствует product_id."))

    return redirect("comparison:comparison")
