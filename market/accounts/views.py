"""
Модуль, содержащий представления для работы с учетными записями пользователей.

Модуль включает в себя следующие классы и функции:

- ProfileView: вью для изменения пароля и email.
- AcountView: вью для страницы пользователя.
- RegistrationView: вью класс для регистрации новых пользователей.
- MyLoginView: вью для аутентификации пользователей.
- PasswordReset: представление для сброса пароля.
- UpdatePasswordView: представление для обновления пароля.
- UserHistoryView: представление истории просмотров пользователя.
- logout_view: функция для выхода из учетной записи.

"""

from typing import Any, List

from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
)
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView, TemplateView
from order.models import OrderStatus, Order
from comparison.services import get_comparison_list
from .forms import (RegistrationForm,
                    LoginForm,
                    CustomPasswordForm,
                    ProfilePasswordForm,
                    ResetPasswordEmailForm)
from .models import ViewHistory
from .service import mail
import random


class ProfileView(LoginRequiredMixin, FormView):
    """Представление для изменения пароля и email"""

    template_name = "accounts/profile.jinja2"
    form_class = ProfilePasswordForm
    success_url = reverse_lazy("user:profile")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.error(self.request, _("успешно"))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("не верный ввод полей"))
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class AcountView(LoginRequiredMixin, TemplateView):
    """Представление для страницы пользователя"""

    template_name = "accounts/account.jinja2"

    def get_context_data(self, **kwargs):
        comparison_list = get_comparison_list(self.request.user.id)
        comparison_count = len(comparison_list)
        context = super().get_context_data(**kwargs)
        context["name"] = self.request.user
        context["comparison_count"] = comparison_count
        try:
            if self.request.session[f'{self.request.user.id}']['id']:
                Order.objects.filter(user=self.request.user.id).update(status=OrderStatus.PAID)

                context["paid"] = _("оплачено")
                return context
        except KeyError:
            return context


class RegistrationView(FormView):
    """Представление класс для регистрации"""

    template_name = "accounts/register.jinja2"
    form_class = RegistrationForm
    success_url = reverse_lazy("user:main")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("не валидная форма или такой пользователь уже есть"))
        return super().form_invalid(form)


class MyLoginView(LoginView):
    """Представление для входа пользователя в систему."""

    template_name = "accounts/login.jinja2"
    form_class = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, email=email, password=password)
        if user:
            login(self.request, user)
            return super().form_valid(form)
        else:
            messages.error(self.request, _("нет пользователя с таким Email или неверный пароль"))
            return super().form_invalid(form)


class PasswordReset(FormView):
    """
    Представление для сброса пароля. Отправляет электронное письмо с инструкциями
    по сбросу пароля на указанный электронный адрес.



    success_url: str
        URL-адрес, на который перенаправляется пользователь после успешного
        запроса на сброс пароля.
    """

    template_name = "accounts/e-mail.jinja2"
    form_class = ResetPasswordEmailForm
    success_url = reverse_lazy("user:reset_password_done")

    def form_valid(self, form):
        """
        Обработчик вызывается при успешном вводе данных в форму.
        Перед отправкой электронного письма проверяет наличие пользователя
        с указанным адресом электронной почты.

        Parameters:
        - form: Form
            Форма с введенными данными.

        Returns:
        - HttpResponseRedirect
            Перенаправляет пользователя на страницу успешного запроса на сброс пароля.
        """
        email = form.cleaned_data["email"]
        try:
            email = get_user_model().objects.get(email=email)
            random_numbers = [random.randint(0, 9) for _ in range(4)]
            random_number = int(''.join(map(str, random_numbers)))
            token_session = mail(email, random_number)
            self.request.session[token_session] = {}
            self.request.session[token_session] = {"check_number": random_number,
                                                   "email": f'{email}',
                                                   }
        except ObjectDoesNotExist:
            messages.error(self.request, "нет пользователя с таким Email")
            return self.form_invalid(form)

        return super().form_valid(form)


class UpdatePasswordView(FormView):
    """
    Представление для обновления пароля. Позволяет пользователю изменить свой пароль
    после успешного запроса на сброс.


    success_url: str
        URL-адрес, на который перенаправляется пользователь после успешного
        обновления пароля.
    """

    model = get_user_model()
    template_name = "accounts/password.jinja2"
    form_class = CustomPasswordForm
    success_url = reverse_lazy("user:login")

    def dispatch(self, request, *args, **kwargs):
        token = kwargs.get('token')  # Получаем токен из kwargs
        session_data = request.session.get(token)
        if not session_data:
            raise Http404()
        email = session_data.get('email')
        get_object_or_404(get_user_model(), email=email)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        """
              Обработчик вызывается при успешном вводе нового пароля.
              Сохраняет новый пароль пользователя.

              Parameters:
              - form: Form
                  Форма с введенным новым паролем.


              """
        token = self.kwargs['token']
        code = self.request.session[f"{token}"]['check_number']
        if code == form.cleaned_data['code']:
            form.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        Обработчик вызывается при ошибке ввода нового пароля.
        Добавляет сообщение об ошибке в систему сообщений Django.

        Parameters:
        - form: Form
            Форма с ошибками.

        Returns:
        - HttpResponseRedirect
            Перенаправляет пользователя на страницу с формой обновления пароля.
        """
        print(form.cleaned_data)
        messages.error(self.request, _("пароли не совпадают или неверный код"))
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        token = self.kwargs['token']
        user = get_user_model().objects.get(email=self.request.session[f"{token}"]['email'])
        kwargs['user'] = user  # Передаем текущего пользователя в форму
        kwargs['data'] = self.request.POST  # Передаем данные запроса в форму
        return kwargs


class UserHistoryView(LoginRequiredMixin, View):
    """Представление истории просмотров пользователя."""

    template_name: str = "accounts/viewing_history.jinja2"

    def get(self, request) -> Any:
        user = request.user
        user_history = ViewHistory.objects.filter(user=user).order_by("-view_date")
        viewed_products: List[Any] = [history.product for history in user_history]

        return render(request, self.template_name, {"viewed_products": viewed_products})


def logout_view(request):
    """Представление для выхода из учетной записи"""
    logout(request)
    return HttpResponseRedirect(reverse("products:index"))
