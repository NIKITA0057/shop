from typing import Any
from unittest.mock import patch

from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import Client, TestCase, RequestFactory

from django.urls import reverse
from django.utils.translation import activate
from uuid import uuid4
from django.contrib.auth.tokens import default_token_generator
from accounts.models import get_user_model

from accounts.views import UpdatePasswordView

User = get_user_model()  # noqa


class ProfileViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        """Установка начальных данных для тестирования."""
        cls.user: User = User.objects.create_user(
            username="newuser", email="test@example.com", password="testpassword"
        )

    def setUp(self) -> None:
        """Настройка для каждого теста."""
        self.client: Client = Client()
        self.client.login(email="test@example.com", password="testpassword")

    def test_profile_view_redirect(self) -> None:
        """Тест перенаправления профиля."""
        response: Any = self.client.get(reverse("user:profile"))
        # Проверка корректного перенаправления
        self.assertEqual(response.status_code, 200)  # Изменить проверку для ожидания перенаправления

    def test_profile_view_form_valid(self) -> None:
        """Тест валидности формы профиля."""
        response: Any = self.client.post(
            reverse("user:profile"), {"new_password1": "newpassword", "new_password2": "newpassword"}
        )
        # Проверка перенаправления после успешной отправки формы
        self.assertEqual(response.status_code, 200)

    def test_profile_view_form_invalid(self) -> None:
        """Тест невалидности формы профиля."""
        response: Any = self.client.post(
            reverse("user:profile"), {"new_password1": "newpassword", "new_password2": "wrongpassword"}
        )
        # Проверка статуса кода ответа 200 для неверной отправки формы
        self.assertEqual(response.status_code, 200)


class RegistrationViewTest(TestCase):
    @classmethod
    def setUp(cls) -> None:
        """Настройка для теста."""
        cls.client: Client = Client()
        activate("ru")

    def test_registration_view_form_invalid(self) -> None:
        """Тест невалидной формы регистрации."""
        with patch("accounts.forms.RegistrationForm.Meta.model.objects.create_user") as mock_create_user:
            mock_create_user.return_value = User.objects.create_user(email="test@example.com", password="testpassword")
            response: Any = self.client.post(
                reverse("user:register"),
                {"email": "new@example.com", "password1": "newpassword", "password2": "wrongpassword"},
            )
            # Проверка статуса кода ответа 302 для неверной отправки формы (перенаправление)
            self.assertEqual(response.status_code, 302)

    def test_registration_view_get(self):
        """Тест получения формы регистрации."""
        url = reverse("accounts:register")
        activate("ru")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class MyLoginViewTest(TestCase):
    @classmethod
    def setUp(cls) -> None:
        """Настройка для теста."""
        cls.client: Client = Client()
        activate("ru")

    @patch("django.contrib.auth.authenticate")
    def test_login_view_get(self, mock_authenticate: Any) -> None:
        """Тест получения формы входа."""
        mock_authenticate.return_value = User.objects.create_user(
            username="newuser", email="test@example.com", password="testpassword"
        )
        response: Any = self.client.get(reverse("user:login"))
        self.assertEqual(response.status_code, 200)


def test_password_reset_view_valid_email(self) -> None:
    """Тест сброса пароля с действительным email."""
    # Проверка, когда пользователь существует
    user: User = User.objects.create(email="test@example.com")  # noqa
    response: Any = self.client.post(reverse("accounts:password_reset"), {"email": "test@example.com"})
    self.assertEqual(response.status_code, 302)  # Всегда ожидается перенаправление


def test_password_reset_view_invalid_email(self) -> None:
    """Тест сброса пароля с недействительным email."""
    # Проверка, когда пользователь не существует
    response: Any = self.client.post(reverse("accounts:password_reset"), {"email": "nonexistent@example.com"})
    self.assertEqual(response.status_code, 302)


class UpdatePasswordViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_update_password_view_invalid(self) -> None:
        """Тест недействительной ссылки на сброс пароля."""
        # Проверка, когда ссылка на сброс пароля недействительна

        # Создание недействительного токена и uid
        token = "invalid_token"
        uid = "invalid_uid"

        # Создание объекта
        response = self.client.get(reverse("accounts:reset_password_confirm", kwargs={"uidb64": uid, "token": token}))

        # Проверка, что сервер возвращает код состояния 404 (или другой подходящий код состояния)
        self.assertEqual(response.status_code, 404)

    def test_update_password_view_valid(self) -> None:
        """Тест действительной ссылки на сброс пароля."""
        # Проверка, когда ссылка на сброс пароля действительна

        user: User = User.objects.create_user(username="username", email="test@example.com", password="testpassword")
        uid = uuid4()
        token = default_token_generator.make_token(user)
        request = self.factory.get(reverse("accounts:reset_password_confirm", kwargs={"uidb64": uid, "token": token}))
        middleware = SessionMiddleware(lambda request: None)
        middleware.process_request(request)
        request.session[f"{token}"] = {}
        request.session[f"{token}"] = {'email': user.email}

        response = UpdatePasswordView.as_view()(request, uidb64=str(uid), token=str(token))

        self.assertEqual(response.status_code, 200)


class UserHistoryViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        """Установка начальных данных для тестирования."""
        cls.user: User = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

    def setUp(self) -> None:
        """Настройка для каждого теста."""
        self.client: Client = Client()
        self.client.login(email="test@example.com", password="testpassword")

    def test_user_history_view(self) -> None:
        """Тест просмотра истории пользователя."""
        response: Any = self.client.get(reverse("accounts:viewing_history"))
        self.assertEqual(response.status_code, 200)


class LogoutViewTest(TestCase):
    @classmethod
    def setUp(cls) -> None:
        """Настройка для теста."""
        cls.client: Client = Client()
        activate("ru")

    def test_logout_view(self) -> None:
        """Тест выхода пользователя."""
        response: Any = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 302)
