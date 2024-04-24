"""Настройки админ панели приложения accounts"""
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from .models import User, ViewHistory


class GroupMemberInline(admin.TabularInline):
    """
    Класс для табличного представеления участников группы в административном интерфейсе.
    """

    model = Group.user_set.through
    verbose_name = "участник"
    verbose_name_plural = "участники"


class GroupAdmin(BaseGroupAdmin):
    """
    Административный класс для управления группами и их участниками.
    """

    inlines = (GroupMemberInline,)


admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Администратор для управления пользователями.

    Поля:

    email: адрес электронной почты пользователя
    is_superuser: признак суперпользователя
    password: пароль пользователя
    """

    list_display = ("email", "is_superuser", "password")


@admin.register(ViewHistory)
class ViewHistoryAdmin(admin.ModelAdmin):
    """
    Администратор для  истории просмотров пользователей.

    Поля:

    user: пользователь, просматривающий товар
    product: товар, просматриваемый пользователем
    view_date: дата и время просмотра
    view_count: количество просмотров
    """

    list_display = ("user", "product", "view_date", "view_count")
