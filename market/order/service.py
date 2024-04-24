"""
Модуль для работы с заказами.

Модуль содержит сервис для работы с заказами и функцию для перевода типа доставки.

"""

from django.db.models import QuerySet
from .models import Order
from cart.cart import CartInstance


def translate(type_delivery):
    if type_delivery == "regular":
        type_delivery = "обычная доставка"
    else:
        type_delivery = "экспресс-доставка"
    type_pay = "онлайн картой"
    return type_delivery, type_pay


class OrderService:
    """Сервис для работы с заказами"""

    def __init__(self, request):
        self.request = request
        self.cart = CartInstance(request).cart

    def get_order_by_id(self, id_: int) -> Order:
        """
        Возвращает заказ по id
        :return: заказ пользователя
        """
        return Order.objects.get(id=id_)

    def get_order_history(self) -> QuerySet[Order]:
        """
        Возвращает историю заказов
        :return: история заказов
        """
        return Order.objects.select_related("cart__user").filter(cart__user=self.cart.user).order_by("-created_at")

    def get_status(self, order: Order) -> str:
        """
        Получение статуса заказа
        :param order: объект заказа
        :return: статус заказа
        """
        return order.status
