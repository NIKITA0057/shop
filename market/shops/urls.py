""" Модуль для определения URL-путей приложения shops """

from django.urls import path

from shops.views import ShopView, ShopCreate, ShopRemove

urlpatterns = [
    path("", ShopView.as_view(), name="shop_dashboard"),
    path("create_shop/", ShopCreate.as_view(), name="shop_create"),
    path("remove_shop/", ShopRemove.as_view(), name="shop_remove"),
]
