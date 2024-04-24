"""Тесты представлений приложения cart"""

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.urls import reverse

from cart.models import Cart, ProductInCart
from cart.views import cart_add, cart_remove
from products.models import Category, Product
from shops.models import Shop, Offer

User = get_user_model()


class CartViewTest(TestCase):
    """Класс тестирования представления страницы корзины"""

    @classmethod
    def setUpTestData(cls) -> None:
        """Настройка данных для тестов"""

        cls.user: User = User.objects.create_user(username="testuser", password="12345")

        cls.category = Category.objects.create(name="Товары")

        cls.product1 = Product.objects.create(name="Продукт", category=cls.category, description="Описание1")
        cls.product2 = Product.objects.create(name="Продукт2", category=cls.category, description="Описание2")
        cls.shop = Shop.objects.create(user=cls.user, name="Магазин")
        cls.offer = Offer.objects.create(shop=cls.shop, product=cls.product1, price=10, remains=1)
        Offer.objects.create(shop=cls.shop, product=cls.product2, price=10, remains=1)

    def setUp(self) -> None:
        """
        Настройка клиента для тестов.
        """
        self.factory = RequestFactory()

    def test_add_to_cart_view(self) -> None:
        """Тестирование представления для добавления товаров в корзину"""

        request = self.factory.post(
            reverse("cart:cart-add", kwargs={"pk": self.product1.id}),
            {"quantity": 1, "offer": self.offer.id},
            HTTP_REFERER="http://foo/bar",
        )
        request.user = self.user
        request.session = {}

        qs = ProductInCart.objects.all()
        self.assertEqual(len(qs), 0)

        response = cart_add(request, pk=self.product1.id)
        self.assertEqual(response.status_code, 302)

        qs = ProductInCart.objects.all()
        self.assertEqual(len(qs), 1)

    def test_remove_from_cart_view(self) -> None:
        """Тестирование представления для удаления товаров из корзины"""

        cart = Cart.objects.create(user=self.user)
        ProductInCart.objects.create(offer=self.offer, cart=cart, quantity=1)
        request = self.factory.post(reverse("cart:cart-remove", kwargs={"pk": self.product1.id}))
        request.user = self.user
        request.session = {}

        qs = ProductInCart.objects.all()
        self.assertEqual(len(qs), 1)

        response = cart_remove(request, pk=self.product1.id)
        self.assertEqual(response.status_code, 302)

        qs = ProductInCart.objects.all()
        self.assertEqual(len(qs), 0)
