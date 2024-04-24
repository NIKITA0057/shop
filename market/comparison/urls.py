# pylint: disable=C0103
""" Модуль для определения URL-путей приложения comparison """
from django.urls import path

from comparison.views import ComparisonView, add_to_comparison, remove_from_comparison_view

urlpatterns = [
    path("", ComparisonView.as_view(), name="comparison"),
    path("add_to_comparison/<int:product_id>/", add_to_comparison, name="add_to_comparison"),
    path("comparison/remove/", remove_from_comparison_view, name="remove_from_comparison"),
]
