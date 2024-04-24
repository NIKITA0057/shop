""" Представления приложения products """
import logging
from typing import Any, Dict, Type

from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Avg, Sum
from django.db.models.functions import Round
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.http import JsonResponse, HttpRequest, HttpResponseNotFound
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, TemplateView
from django_filters.views import FilterView

from accounts.models import ViewHistory
from cart.cart import CartInstance
from cart.forms import CartAddProductForm
from comparison.services import get_comparison_list
from products.services.mainpage_services import MainPageService
from products.services.review_services import ReviewService

from shops.models import Offer, Shop
from . import constants
from .filters import ProductFilter
from .forms import ReviewsForm, CartAddProductCatalogForm
from .models import Product, ProductImage, Review
from .services.catalog_services import (
    get_popular_tags,
    get_paginate_products_by,
    get_full_path_of_request_without_param_page,
)
from .services.product_services import (
    get_discount_for_product,
    invalidate_product_details_cache,
    get_from_cache_or_set,
)

logger = logging.getLogger(__name__)


def add_product_to_cart(request: HttpRequest, cart_form: CartAddProductCatalogForm) -> None:
    """Добавляет товар в корзину на главной странице и каталога"""
    product_id = request.POST["product_id"]
    product = Product.objects.get(pk=product_id)
    quantity = cart_form.cleaned_data["quantity"]
    cart = CartInstance(request)
    cart.add(
        product=product,
        offer=None,
        quantity=quantity,
        update_quantity=True,
    )


class MainPageView(TemplateView):
    """Класс представление главной страницы"""

    template_name = "products/index.jinja2"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request is not None:
            comparison_list = get_comparison_list(self.request.user.id)
            comparison_count = len(comparison_list)
        else:
            comparison_count = 0

        main_page_service = MainPageService()
        context["banners"] = main_page_service.banners_cache()
        context["top_products"] = main_page_service.get_top_products()
        context["top_categories"] = main_page_service.get_top_categories()
        context["hot_offers"] = main_page_service.get_hot_offers()
        context["limited_products"] = main_page_service.get_limited_products()
        context["product_of_day"] = main_page_service.get_product_of_day()
        context["comparison_count"] = comparison_count
        context["cart_form"] = CartAddProductCatalogForm()
        context["time_to_midnight"] = main_page_service.get_tomorrow_date()
        return context

    def post(self, request: HttpRequest, **kwargs):
        cart_form = CartAddProductCatalogForm(request.POST)
        if cart_form.is_valid():
            add_product_to_cart(request, cart_form)
        return redirect("products:index")


class CatalogView(FilterView):
    """Представление для каталога товаров"""

    template_name = "products/catalog.jinja2"
    filterset_class = ProductFilter
    paginate_by = get_paginate_products_by()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["tags"] = get_popular_tags()
        context["cart_form"] = CartAddProductCatalogForm()
        context["relative_url"] = get_full_path_of_request_without_param_page(self.request)

        return context

    def get_queryset(self):
        return (
            Product.objects.all()
            .annotate(avg_price=Round(Avg("offer__price"), constants.DECIMAL_PRECISION))
            .annotate(remains=Sum("offer__remains"))
        ).exclude(avg_price=None)

    def post(self, request: HttpRequest):
        cart_form = CartAddProductCatalogForm(request.POST)
        if cart_form.is_valid():
            add_product_to_cart(request, cart_form)
        return redirect("products:catalog")


def add_to_view_history(request, product: Product):
    """
    Функция добавляет информацию о просмотре товара в историю просмотров пользователя.

    """
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "User is not authenticated"})

    view_history, created = ViewHistory.objects.get_or_create(user=request.user, product=product)

    if not created:
        view_history.view_count += 1
        view_history.view_date = timezone.now()
    else:
        view_history.view_count = 1

    view_history.save()
    return JsonResponse({"status": "success"})


@receiver([post_save, post_delete], sender=Product)
def clear_product_detail_cache(sender: Type[Product], instance: Product, **kwargs) -> None:
    """Очистка кэша с характеристиками продукта"""
    invalidate_product_details_cache(instance.pk)


class ProductDetailView(DetailView):
    """
    Представление для детальной страницы продукта.

    Атрибуты:
    - template_name (str): Имя шаблона для отображения страницы продукта.
    - model: Класс модели для этого представления.
    - context_object_name: Имя переменной контекста для объекта модели.
    """

    template_name = "products/product.jinja2"
    model = Product
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review_service = ReviewService(self.request, self.request.user, self.get_object())
        product = self.object

        context["product"] = get_from_cache_or_set(product.pk)
        context["offers"] = Offer.objects.filter(product=product).order_by("price")
        context["discount"] = get_discount_for_product(product)
        context["shops"] = Shop.objects.filter(products=product)
        context["images"] = ProductImage.objects.filter(product=product)
        context["reviews"] = review_service.get_reviews_for_product()
        context["paginator"], context["page_obj"] = review_service.paginate(context["reviews"])
        context["review_form"] = ReviewsForm()
        context["cart_form"] = CartAddProductForm(initial={"quantity": 1})
        return context

    def dispatch(self, *args, **kwargs):
        product = self.get_object()
        add_to_view_history(self.request, product)
        return super().dispatch(*args, **kwargs)

    def post(self, request: HttpRequest, **kwargs):
        cart_form = CartAddProductForm(request.POST)
        if cart_form.is_valid():
            product_id = kwargs["pk"]
            product = Product.objects.get(pk=product_id)
            quantity = cart_form.cleaned_data["quantity"]
            offer_id = request.POST["offer"]
            offer = None
            if offer_id:
                offer = Offer.objects.get(pk=offer_id)
            cart = CartInstance(request)
            cart.add(
                product=product,
                offer=offer,
                quantity=quantity,
                update_quantity=True,
            )
            return redirect("products:product-details", pk=product.pk)

        return HttpResponseNotFound(_("Ошибка!"))


def add_review(request: WSGIRequest):
    """
    Добавляет отзыв о товаре
    :param request: POST запрос
    :return: обновляет страницу
    """
    if request.method == "POST":
        form = ReviewsForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data["product"].id
            existing_review = Review.objects.filter(user=request.user, product_id=product_id).exists()
            if not existing_review:
                product = Product.objects.get(id=product_id)
                review = ReviewService(request, request.user, product)
                text = form.cleaned_data["text"]
                rating = form.cleaned_data["rating"]
                try:
                    review.add(text=text, rating=rating)
                    messages.success(request, "Отзыв успешно добавлен.")
                except Exception as e:
                    logger.exception("Ошибка при добавлении отзыва: %s", str(e))
                    messages.error(request, "Произошла ошибка при добавлении отзыва.")
            else:
                messages.error(request, "Вы уже добавили отзыв на этот товар.")

    return redirect(request.META.get("HTTP_REFERER"))
