"""
Модуль, содержащий миксины для проверки принадлежности пользователей к определенным группам.

Classes:
    GroupRequiredMixin: Миксин, требующий принадлежности пользователя к определенным группам.
    SellersRequiredMixin: Миксин, требующий принадлежности пользователя к группе "Sellers".
    BuyersRequiredMixin: Миксин, требующий принадлежности пользователя к группе "Buyers".
"""
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.urls import reverse_lazy


class BaseRequiredMixin(UserPassesTestMixin):
    """
    Базовый миксин для проверки принадлежности пользователя к определенной группе
    и авторизации.
    """

    def test_func(self):
        user = self.request.user
        if user.is_authenticated:
            return self.check_group(user)
        else:
            return redirect(reverse_lazy("login"))


class GroupRequiredMixin(BaseRequiredMixin):
    """
    Миксин, который требует, чтобы пользователь был членом определенной группы.
    """

    def test_func(self):
        user = self.request.user
        if Group.objects.filter(user=user, name__in=["Sellers", "Buyers"]).exists():
            return True
        return False


class SellersRequiredMixin(BaseRequiredMixin):
    """
    Миксин, который требует, чтобы пользователь был продавцом.
    """

    def test_func(self):
        user = self.request.user
        if Group.objects.filter(user=user, name="Sellers").exists():
            return True
        return False


class BuyersRequiredMixin(BaseRequiredMixin):
    """
    Миксин, который требует, чтобы пользователь был покупателем.
    """

    def test_func(self):
        user = self.request.user
        if Group.objects.filter(user=user, name="Buyers").exists():
            return True
        return False
