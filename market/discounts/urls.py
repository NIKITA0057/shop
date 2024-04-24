# pylint: disable=C0103
""" Модуль для определения URL-путей приложения discounts """
from django.urls import path

from discounts.views import (
    DiscountListView,
    DiscountProductDetailView,
    DiscountCartDetailView,
    DiscountSetDetailView,
)

app_name = "discounts"

urlpatterns = [
    path("", DiscountListView.as_view(), name="discount-list"),
    path("products/<int:pk>/", DiscountProductDetailView.as_view(), name="discount-product-details"),
    path("sets/<int:pk>/", DiscountSetDetailView.as_view(), name="discount-set-details"),
    path("cart/<int:pk>/", DiscountCartDetailView.as_view(), name="discount-cart-details"),
]
