"""
Модуль для представлений настроек сайта.
"""

from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from .forms import SiteSettingsForm
from .models import SiteSettings


def is_admin(user: Any) -> bool:
    """Проверяет, является ли пользователь администратором."""
    return user.is_superuser


@method_decorator(user_passes_test(is_admin), name="dispatch")
class SettingsView(TemplateView):
    """Представление для редактирования настроек сайта."""

    template_name = "settings_app/settings.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Получает контекст данных для шаблона."""
        site_settings, created = SiteSettings.objects.get_or_create()
        form = SiteSettingsForm(instance=site_settings)

        return {
            "form1": form,
            "site_settings": site_settings,
            "app_label": "settings_app",
        }

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Обрабатывает POST-запрос для сохранения настроек."""
        site_settings, created = SiteSettings.objects.get_or_create()

        form = SiteSettingsForm(request.POST, instance=site_settings)
        if form.is_valid():
            form.save()
            messages.success(request, _("Настройки успешно обновлены"))
            return redirect(reverse("admin:index"))

        messages.error(request, _("Ошибка при обновлении настроек. Пожалуйста, исправьте ошибки."))
        return self.render_to_response(self.get_context_data(form=form))


@method_decorator(user_passes_test(lambda u: u.is_superuser), name="dispatch")
class ResetCacheView(View):
    """Представление для сброса кэша."""

    template_name = "settings_app/reset_cache.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        """Обрабатывает GET-запрос для отображения страницы сброса кэша."""
        return render(request, self.template_name)

    def post(self, request: HttpRequest) -> HttpResponse:
        """Обрабатывает POST-запрос для сброса кэша."""
        cache.clear()
        messages.success(request, _("Весь кэш успешно очищен"))

        return redirect(reverse("admin:index"))
