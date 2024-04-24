from typing import List

from django.test import TestCase

from accounts.models import User
from cart.models import Cart
from order.models import Order, OrderStatus, PaymentTypes, DeliveryTypes


class OrderModelTest(TestCase):
    """
    Класс тестирования модели заказа.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """
        Настройка данных для тестов.
        """
        # Создание пользователя
        cls.user: User = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

        # Создание корзины
        cls.cart: Cart = Cart.objects.create(user=cls.user)

        # Создание заказа
        cls.order: Order = Order.objects.create(
            name="Test Name",
            phone="1234567890",
            user=cls.user,
            city="Test City",
            address="Test Address",
            cart=cls.cart,
            total_price=100.0,
        )

    def test_order_creation(self) -> None:
        """
        Тестирование создания заказа.
        """
        # Проверка, что экземпляр заказа создан корректно
        self.assertEqual(self.order.name, "Test Name")
        self.assertEqual(self.order.phone, "1234567890")
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.city, "Test City")
        self.assertEqual(self.order.address, "Test Address")
        self.assertEqual(self.order.cart, self.cart)
        self.assertEqual(self.order.total_price, 100.0)

    def test_order_status_choices(self) -> None:
        """
        Тестирование выбора статуса заказа.
        """
        # Тестирование выбора для OrderStatus
        expected_status_choices: List[str] = ["created", "paid", "not_paid"]
        actual_status_choices: List[str] = [choice[0] for choice in OrderStatus.choices]
        self.assertEqual(actual_status_choices, expected_status_choices)

    def test_payment_types_choices(self) -> None:
        """
        Тестирование выбора типа оплаты.
        """
        # Тестирование выбора для PaymentTypes
        expected_payment_types_choices: List[str] = ["card"]
        actual_payment_types_choices: List[str] = [choice[0] for choice in PaymentTypes.choices]
        self.assertEqual(actual_payment_types_choices, expected_payment_types_choices)

    def test_delivery_types_choices(self) -> None:
        """
        Тестирование выбора типа доставки.
        """
        # Тестирование выбора для DeliveryTypes
        expected_delivery_types_choices: List[str] = ["regular", "express"]
        actual_delivery_types_choices: List[str] = [choice[0] for choice in DeliveryTypes.choices]
        self.assertEqual(actual_delivery_types_choices, expected_delivery_types_choices)

    def test_order_verbose_names(self) -> None:
        """
        Тестирование verbose names модели заказа.
        """
        # Проверка verbose names для модели Order
        self.assertEqual(Order._meta.verbose_name, "заказ")
        self.assertEqual(Order._meta.verbose_name_plural, "заказы")
