"""Тесты моделей приложения cart"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from cart.models import Cart, ProductInCart
from products.models import Product, Category
from shops.models import Offer, Shop

UserModel = get_user_model()


class CartModelTest(TestCase):
    """Класс для тестирования модели корзины"""

    @classmethod
    def setUpTestData(cls) -> None:
        """Настройка начальных данных для теста."""
        cls.user: User = UserModel.objects.create_user(
            username="test_user", email="test@example.com", password="test_password"
        )
        cls.cart: Cart = Cart.objects.create(user=cls.user)

    def test_cart_creation(self) -> None:
        """Тест создания корзины."""
        self.assertTrue(isinstance(self.cart, Cart))
        self.assertEqual(self.cart.__str__(), f"Cart {self.user}")

    def test_cart_is_active_default(self) -> None:
        """Тест активности корзины по умолчанию."""
        self.assertTrue(self.cart.is_active)

    def test_cart_user_relationship(self) -> None:
        """Тест связи с пользователем."""
        self.assertEqual(self.cart.user, self.user)


class ProductInCartModelTest(TestCase):
    """Класс для тестирования модели продукта в корзине"""

    @classmethod
    def setUpTestData(cls) -> None:
        """Настройка начальных данных для теста."""
        cls.user: User = UserModel.objects.create_user(
            username="test_user", email="test@example.com", password="test_password"
        )
        cls.shop: Shop = Shop.objects.create(name="Test Shop", user=cls.user)
        cls.category: Category = Category.objects.create(name="Test Category")
        cls.product: Product = Product.objects.create(name="Test Product", category=cls.category)
        cls.offer: Offer = Offer.objects.create(product=cls.product, price=10, shop=cls.shop)
        cls.cart: Cart = Cart.objects.create(user=cls.user)
        cls.product_in_cart: ProductInCart = ProductInCart.objects.create(
            offer=cls.offer, cart=cls.cart, quantity=1, created_at=timezone.now()
        )

    def test_product_in_cart_creation(self) -> None:
        """Тест создания продукта в корзине."""
        self.assertTrue(isinstance(self.product_in_cart, ProductInCart))
        self.assertEqual(self.product_in_cart.__str__(), f"Product {self.offer.product} in cart {self.cart}")

    def test_product_in_cart_quantity(self) -> None:
        """Тест количества продукта в корзине."""
        self.assertEqual(self.product_in_cart.quantity, 1)

    def test_product_in_cart_offer_relationship(self) -> None:
        """Тест связи с предложением."""
        self.assertEqual(self.product_in_cart.offer, self.offer)

    def test_product_in_cart_cart_relationship(self) -> None:
        """Тест связи с корзиной."""
        self.assertEqual(self.product_in_cart.cart, self.cart)
