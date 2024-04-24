# pylint: disable=C0103
""" Модуль для определения URL-путей приложения products """

from django.urls import path
from .views import MainPageView, ProductDetailView, add_review, CatalogView

urlpatterns = [
    path("", MainPageView.as_view(), name="index"),
    path("add_review/", add_review, name="add_review"),
    path("<int:pk>/", ProductDetailView.as_view(), name="product-details"),
    path("catalog/", CatalogView.as_view(), name="catalog"),
]
