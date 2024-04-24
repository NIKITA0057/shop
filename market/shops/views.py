"""Модуль, содержащий представления для управления магазинами."""

from typing import Any

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from .forms import ShopForm
from .models import Shop
from .services.services import create_shop, remove_shop


class ShopView(TemplateView):
    """Представление для отображения информации о магазине."""

    template_name: str = "shops/shop_dashboard.jinja2"

    @staticmethod
    @login_required
    def get(request: HttpRequest) -> HttpResponse:
        """
        GET-запрос к представлению.

        Отображает информацию о магазине пользователя.

        :param request: Запрос.
        :return: Ответ с информацией о магазине.
        """
        user: Any = request.user
        try:
            shop: Shop = Shop.objects.get(user=user)
            context: dict = {
                "shop": shop,
                "products": shop.products.all(),
                "offers": shop.offer_set.all(),
                "imports": user.imports.all(),
            }
            return render(request, "shops/shop_dashboard.jinja2", context)
        except Shop.DoesNotExist:
            return redirect("shops:shop_create")


class ShopCreate(TemplateView):
    """Представление для создания нового магазина."""

    template_name: str = "shops/create_shop.jinja2"

    @staticmethod
    @login_required
    def get(request: HttpRequest) -> HttpResponse:
        """
        GET-запрос к представлению.

        Отображает форму для создания нового магазина.

        :param request: Запрос.
        :return: Ответ с формой создания магазина.
        """
        form: ShopForm = ShopForm()
        return render(request, "shops/create_shop.jinja2", {"form": form})

    @staticmethod
    @login_required
    def post(request: HttpRequest) -> HttpResponse:
        """
        POST-запрос к представлению.

        Обрабатывает форму создания нового магазина.

        :param request: Запрос.
        :return: Редирект на панель управления магазином.
        """
        user: Any = request.user
        form: ShopForm = ShopForm(request.POST, request.FILES)
        if form.is_valid():
            create_shop(user, form.cleaned_data)
            return redirect("shops:shop_dashboard")
        return render(request, "shops/create_shop.jinja2", {"form": form})


class ShopRemove(TemplateView):
    """Представление для удаления магазина."""

    template_name: str = "shops/remove_shop.jinja2"

    @staticmethod
    @login_required
    def get(request: HttpRequest) -> HttpResponse:
        """
        GET-запрос к представлению.

        Отображает подтверждение удаления магазина.

        :param request: Запрос.
        :return: Ответ с подтверждением удаления магазина.
        """
        return render(request, "shops/remove_shop.jinja2")

    @staticmethod
    @login_required
    def post(request: HttpRequest) -> HttpResponse:
        """
        POST-запрос к представлению.

        Удаляет магазин пользователя.

        :param request: Запрос.
        :return: Редирект на панель управления магазином.
        """
        user: Any = request.user
        try:
            shop: Shop = Shop.objects.get(user=user)
            remove_shop(shop)
        except Shop.DoesNotExist:
            pass
        return redirect("shops:shop_dashboard")
