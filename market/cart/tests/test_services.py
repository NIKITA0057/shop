"""Тесты сервисов приложения cart"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, Client

from cart.cart import CartInstance
from cart.models import ProductInCart
from discounts.models import DiscountProduct, DiscountCart, DiscountSet
from products.models import Category, Product
from shops.models import Offer, Shop

User = get_user_model()


class CartTests(TestCase):
    """Тесты класса CartInstance"""

    @classmethod
    def setUpTestData(cls):
        """Подготовка тестовых данных"""

        cls.user = User.objects.create_user(username="testuser", password="12345")

        cls.category = Category.objects.create(name="Товары")
        cls.product1 = Product.objects.create(name="Продукт", category=cls.category, description="Описание")
        cls.product2 = Product.objects.create(name="Продукт2", category=cls.category, description="Описание2")
        cls.shop = Shop.objects.create(user=cls.user, name="Магазин")
        cls.offer = Offer.objects.create(shop=cls.shop, product=cls.product1, price=10, remains=1)
        Offer.objects.create(shop=cls.shop, product=cls.product2, price=10, remains=1)

    def setUp(self) -> None:
        """Настройка клиента для тестов."""
        self.client = Client()
        self.offer = Offer.objects.first()
        self.request = self.client.get("/")
        self.request.session = self.client.session
        self.request.user = User.objects.first()
        self.cart = CartInstance(self.request)

    def test_add_for_authenticated_user(self) -> None:
        """Тестирование добавления товара в корзину для авторизованного пользователя"""

        self.cart.add(product=self.offer.product, offer=self.offer, quantity=1)
        added_offer = ProductInCart.objects.first()
        self.assertEqual(self.offer, added_offer.offer)
        self.assertEqual(added_offer.quantity, 1)
        self.assertEqual(added_offer.offer.product, self.offer.product)
        self.assertEqual(len(self.cart), 1)

    def test_remove_for_authenticated_user(self) -> None:
        """Тестирование удаления товара из корзины для авторизованного пользователя"""

        self.cart.add(product=self.offer.product, offer=self.offer, quantity=1)
        qs = ProductInCart.objects.all()
        self.assertEqual(len(qs), 1)

        self.cart.remove(self.offer)

        qs = ProductInCart.objects.all()
        self.assertEqual(len(qs), 0)

    def test_clear_for_authenticated_user(self) -> None:
        """Тестирование удаления корзины для авторизованного пользователя"""

        self.cart.add(product=self.offer.product, offer=self.offer, quantity=1)

        is_exist = ProductInCart.objects.all().exists()
        self.assertTrue(is_exist)

        self.cart.clear()
        is_exist = ProductInCart.objects.all().exists()
        self.assertFalse(is_exist)

    def test_add_for_anonymous_user(self) -> None:
        """Тестирование добавления товара в корзину для неавторизованного пользователя"""

        self.request.user = AnonymousUser()
        cart = CartInstance(self.request)

        cart.add(product=self.offer.product, offer=self.offer, quantity=1)
        cart_data = cart.cart

        self.assertIn(str(self.offer.id), cart_data)
        self.assertEqual(cart_data[str(self.offer.id)]["quantity"], 1)
        self.assertEqual(cart_data[str(self.offer.id)]["price"], "10.00")
        self.assertEqual(len(cart), 1)

    def test_remove_for_anonymous_user(self) -> None:
        """Тестирование удаления товара из корзины для неавторизованного пользователя"""

        self.request.user = AnonymousUser()
        cart = CartInstance(self.request)

        cart.add(product=self.offer.product, offer=self.offer, quantity=1)
        self.assertEqual(len(cart), 1)

        cart.remove(self.offer)
        self.assertEqual(len(cart), 0)

    def test_clear_for_anonymous_user(self) -> None:
        """Тестирование удаления корзины для неавторизованного пользователя"""

        self.request.user = AnonymousUser()
        cart = CartInstance(self.request)

        cart.add(product=self.offer.product, offer=self.offer, quantity=1)
        self.assertTrue(len(cart))

        cart.clear(only_session=True)
        self.assertFalse(len(cart))

    def test_transferring_cart_from_session_to_db(self):
        """Тестирование корзины из сессии в базу данных"""

        self.request.user = AnonymousUser()
        cart = CartInstance(self.request)
        cart.add(product=self.offer.product, offer=self.offer, quantity=1)

        qs = ProductInCart.objects.all()
        self.assertEqual(len(qs), 0)

        self.request.user = User.objects.first()
        cart = CartInstance(self.request)

        qs = ProductInCart.objects.all()
        self.assertEqual(len(qs), 1)

    def test_get_total_price_without_discount(self) -> None:
        """Тестирование получения стоимости корзины"""

        self.cart.add(product=self.offer.product, offer=self.offer, quantity=1)
        self.assertTrue(len(self.cart))

        total_price = self.cart.get_total_price()
        self.assertEqual(total_price, Decimal("10"))

    def test_get_total_price_with_product_discount(self) -> None:
        """Тестирование получения стоимости корзины с учетом скидки на товар"""

        discount_product = DiscountProduct.objects.create(
            title="title",
            description="description",
            start_date="2024-03-17",
            end_date="2050-03-03",
            weight=0.2,
            percentage=50,
        )
        discount_product.products.add(self.product1)

        self.cart.add(product=self.offer.product, offer=self.offer, quantity=1)
        self.assertTrue(len(self.cart))

        total_price = self.cart.get_total_price()
        self.assertEqual(total_price, Decimal("5"))

    def test_get_total_price_with_cart_discount(self) -> None:
        """Тестирование получения стоимости корзины с учетом скидки на корзину"""

        d_c = DiscountCart.objects.create(
            title="title",
            description="description",
            start_date="2024-03-17",
            end_date="2050-03-03",
            weight=0.2,
            percentage=50,
            price_from=Decimal("5"),
            price_to=Decimal("15"),
        )

        self.cart.add(product=self.offer.product, offer=self.offer, quantity=1)
        self.assertTrue(len(self.cart))

        total_price = self.cart.get_total_price()
        self.assertEqual(total_price, Decimal("5"))

        d_c.price_from = Decimal("11")
        d_c.save()
        total_price = self.cart.get_total_price()
        self.assertEqual(total_price, Decimal("10"))

    def test_get_total_price_with_set_discount(self) -> None:
        """Тестирование получения стоимости корзины с учетом скидки на наборы"""

        discount_set = DiscountSet.objects.create(
            title="title",
            description="description",
            start_date="2024-03-17",
            end_date="2050-03-03",
            weight=0.2,
            discount_amount=Decimal("10"),
        )

        discount_set.first_group.add(self.product1)
        discount_set.second_group.add(self.product2)
        discount_set.save()

        self.cart.add(product=self.offer.product, offer=self.offer, quantity=1)
        self.cart.add(product=self.product2, quantity=1)

        total_price = self.cart.get_total_price()
        self.assertEqual(total_price, Decimal("10"))
