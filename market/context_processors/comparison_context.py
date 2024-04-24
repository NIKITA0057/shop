"""
Модуль для работы со сравнениями товаров.

Этот модуль содержит функцию для управления сравнениями товаров.
"""
from comparison.views import ComparisonView


def comparison_count(request):
    """Количество сравнений."""
    comparison_count_value = ComparisonView.comparison_count(request)
    return {"comparison_count": comparison_count_value}
