"""Сервисы приложения cart"""

import random
from decimal import Decimal
from typing import Any

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, F
from django.http import HttpResponseNotFound
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from cart.models import ProductInCart, Cart
from discounts.services import (
    calculate_product_price_with_discount,
    calculate_cart,
    calculate_set,
)
from products.models import Product
from shops.models import Offer


class CartInstance:
    """Класс корзины покупок"""

    def __init__(self, request):
        self.__use_db = False
        self.cart = None
        self.cart_for_view = []
        self.user = request.user
        self.session = request.session
        self.qs = None
        cart = self.session.get(settings.CART_SESSION_ID)
        if self.user.is_authenticated:
            self.__use_db = True
            if cart:
                self.__save_in_db(cart, request.user)
                self.clear(True)
            try:
                cart = Cart.objects.get(user=self.user, is_active=True)
            except ObjectDoesNotExist:
                cart = Cart.objects.create(user=self.user)
            self.qs = ProductInCart.objects.filter(cart=cart)
        else:
            if not cart:
                cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def __save_in_db(self, cart: dict, user: User) -> None:
        """
        Перенос корзины из сессии в БД
        :param cart: корзина из сессии
        :param user: пользователь
        :return: None
        """
        try:
            cart_ = Cart.objects.get(user=user, is_active=True)
            cart_exists = True
        except ObjectDoesNotExist:
            cart_exists = False

        for key, value in cart.items():
            if cart_exists:
                try:
                    product = ProductInCart.objects.filter(cart=cart_).get(offer=key)
                    product.quantity += cart[key]["quantity"]
                    product.save()
                except ObjectDoesNotExist:
                    ProductInCart.objects.create(
                        offer=Offer.objects.get(pk=key),
                        cart=Cart.objects.filter(user=user, is_active=True).first(),
                        quantity=cart[key]["quantity"],
                    )
            else:
                offer = Offer.objects.get(id=key)
                cart_, is_created = Cart.objects.update_or_create(user=user)
                ProductInCart.objects.create(
                    offer=offer,
                    cart=cart_,
                    quantity=value["quantity"],
                )

    def add(self, product: Product, offer: Offer = None, quantity: int = 1, update_quantity: bool = False) -> None:
        """
        Добавляет товар в корзину и обновляет его количество
        :param product: товар
        :param offer: предложение товара
        :param quantity: количество
        :param update_quantity: флаг, указывающий, нужно ли обновить товар (True) либо добавить его (False)
        :return: None
        """
        if not offer:
            offer = self.get_offer(product, quantity)
        if self.__use_db:
            if self.qs.filter(offer=offer).exists():
                product_in_cart = self.qs.get(offer=offer)
            else:
                product_in_cart = ProductInCart(offer=offer, cart=self.cart, quantity=0)
            if update_quantity:
                product_in_cart.quantity += quantity
            else:
                product_in_cart.quantity = quantity
            product_in_cart.quantity = min(product_in_cart.quantity, offer.remains)
            product_in_cart.save()
        else:
            offer_id = str(offer.id)
            if offer_id not in self.cart:
                self.cart[offer_id] = {"quantity": 0, "price": str(offer.price)}
            if update_quantity:
                self.cart[offer_id]["quantity"] += quantity
            else:
                self.cart[offer_id]["quantity"] = quantity
            if self.cart[offer_id]["quantity"] > offer.remains:
                self.cart[offer_id]["quantity"] = offer.remains
            self.save()

    def save(self) -> None:
        """Сохранение корзины в сессии"""
        if not self.__use_db:
            self.session[settings.CART_SESSION_ID] = self.cart
            self.session.modified = True

    def remove(self, offer: Offer) -> None:
        """Удаление товара из корзины"""
        if self.__use_db:
            offer_ = self.qs.filter(offer=offer)
            if offer_.exists():
                offer_.delete()
        else:
            offer_id = str(offer.id)
            if offer_id in self.cart:
                del self.cart[offer_id]
                self.save()

    def __iter__(self):
        """Перебор товаров из корзины"""
        yield from self.__get_discount_cart_items()

    def __len__(self) -> int:
        """Подсчет количество товаров в корзине"""
        if self.__use_db:
            result = ProductInCart.objects.filter(cart=self.cart).aggregate(Sum("quantity"))["quantity__sum"]
            return result if result else 0
        return sum(item["quantity"] for item in self.cart.values())

    def clear(self, only_session: bool = False) -> None:
        """Удаление корзины из сеанса или из базы данных, если пользователь авторизован"""
        if only_session:
            del self.session[settings.CART_SESSION_ID]
            self.cart = {}
            self.session.modified = True
        else:
            if self.qs:
                self.qs.delete()

    def __get_discount_cart_items(self) -> list[dict]:
        """Подготовка списка товаров корзины с учетом скидок"""
        if self.cart_for_view:
            return self.cart_for_view

        discount_type, _ = self.__get_discount_type()
        if discount_type == "product":
            if self.__use_db:
                for product in self.qs:
                    self.cart_for_view.append(
                        {
                            "offer": product.offer,
                            "price": calculate_product_price_with_discount(product.offer) * product.quantity,
                            "quantity": product.quantity,
                        }
                    )
            else:
                for key, value in self.cart.items():
                    offer = Offer.objects.get(pk=key)
                    self.cart_for_view.append(
                        {
                            "offer": offer,
                            "price": calculate_product_price_with_discount(offer) * value["quantity"],
                            "quantity": value["quantity"],
                        }
                    )
        else:
            if self.__use_db:
                for product in self.qs:
                    self.cart_for_view.append(
                        {
                            "offer": product.offer,
                            "price": product.offer.price * product.quantity,
                            "quantity": product.quantity,
                        }
                    )
            else:
                for key, value in self.cart.items():
                    offer = Offer.objects.get(pk=key)
                    self.cart_for_view.append(
                        {"offer": offer, "price": offer.price * value["quantity"], "quantity": value["quantity"]}
                    )
        return self.cart_for_view

    def __get_offers(self):
        """Получение всех товаров из корзины"""

        if self.__use_db:
            return [item.offer for item in self.qs]

        return [Offer.objects.get(pk=int(idx)) for idx in self.cart.keys()]

    def get_offers_with_quantity(self):
        """Получение всех товаров с количеством из корзины"""

        if self.__use_db:
            return [(item.offer, item.quantity) for item in self.qs]

        return [(Offer.objects.get(pk=int(idx)), item["quantity"]) for idx, item in self.cart.items()]

    def get_offer(self, product: Product, quantity: int = 1) -> HttpResponseNotFound | Any:
        """Подбор предложения для товара"""
        if self.__use_db:
            products_in_cart = self.qs.filter(offer__product=product)
            if products_in_cart:
                return products_in_cart[0].offer
        else:
            offers = Offer.objects.filter(product=product)
            for offer in offers:
                if str(offer.id) in self.cart:
                    return offer

        offers = Offer.objects.filter(product=product).filter(remains__gte=quantity)
        if offers:
            return random.choice(offers)
        return HttpResponseNotFound(_("Ошибка! Не хватает товаров на складе!"))

    def get_total_price_without_discount(self) -> Decimal | int:
        """Получение итоговой цены товаров корзины без учета скидок"""
        if self.__use_db:
            total = self.qs.only("quantity").aggregate(total=Sum(F("quantity") * F("offer__price")))["total"]
            if not total:
                total = Decimal("0")
            return total.quantize(Decimal("1.00"))

        return sum(Decimal(item["price"]) * item["quantity"] for item in self.cart.values())

    def __get_discount_type(self) -> tuple[str, int]:
        """Определение типа скидки"""

        total_price = self.get_total_price_without_discount()
        offers = self.__get_offers()

        weight_cart, percentage_cart = calculate_cart(total_price)
        weight_set, discount_cost = calculate_set(offers)

        if weight_cart >= weight_set and weight_cart > 0:
            return "cart", percentage_cart

        if weight_cart < weight_set:
            return "set", discount_cost

        return "product", 0

    def get_total_price(self) -> Decimal:
        """Подсчет стоимости корзины с учетом всех скидок"""

        discount_type, discount = self.__get_discount_type()
        total_price = self.get_total_price_without_discount()

        if discount_type == "cart":
            return total_price - (total_price * discount / 100)

        if discount_type == "set":
            total_price -= discount
            return total_price if total_price > 1 else 1

        return self.__calculate_products_discount_total_price()

    def __calculate_products_discount_total_price(self) -> Decimal | int:
        """Подсчет стоимости корзины с учетом скидок на товары"""
        total_price = 0
        for offer in self.get_offers_with_quantity():
            total_price += calculate_product_price_with_discount(offer[0]) * offer[1]
        return total_price
