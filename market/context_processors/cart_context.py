"""Модуль с глобальным контекстом сайта"""

from cart.cart import CartInstance


def get_cart_cost(request):
    """Стоимость корзины"""
    cart = CartInstance(request)
    return {"cart_cost": cart.get_total_price(), "cart_amount": len(cart)}
