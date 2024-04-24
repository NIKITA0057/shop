"""Сервис для работы с отзывами приложения products"""
from typing import Tuple, Any
from django.db.models import QuerySet
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.http import HttpRequest
from products.models import Review, Product


User = get_user_model()


class ReviewService:
    """Сервис для работы с отзывами"""

    def __init__(self, request: HttpRequest, profile: User, product: Product):
        self.request = request
        self.product = product
        self.profile = profile

    def add(self, text: str, rating: int) -> None:
        """
        Добавляет отзыв к товару
        :param review: текст отзыва о товаре
        :return: None
        """
        Review.objects.create(
            user=self.profile,
            product=self.product,
            text=text,
            rating=rating,
        )

    def get_reviews_for_product(self) -> QuerySet[Review]:
        """
        Возвращает все отзывы о товаре
        :return: список отзывов
        """
        reviews = (
            Review.objects.filter(product=self.product)
            .order_by("-created_at")
            .select_related("user")
            .select_related("product")
        )
        return reviews

    def paginate(self, reviews: QuerySet[Review]) -> Tuple[Paginator, Any]:
        """
        Возвращает пагинатор для работы пагинации отзывов о товарах
        :param reviews: список отзывов о товаре
        :return: пагинатор и объект пагинации
        """
        paginator = Paginator(reviews, 3)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return paginator, page_obj
