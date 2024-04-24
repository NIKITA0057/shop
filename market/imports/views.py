"""
Модуль, содержащий представления и утилиты для обработки импорта товаров.

Этот модуль содержит представления для отображения страницы импорта,
деталей импорта товаров и скачивания шаблона CSV-файла.

Модуль также предоставляет утилиты для обработки импорта.

Классы:
    ImportPageView: Представление для отображения страницы импорта.
    ImportDetailsView: Представление для отображения и обработки деталей импорта товаров.
    DownloadCSVTemplateView: Представление для скачивания шаблона CSV-файла.
"""
import logging
import os

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from settings_app.models import SiteSettings
from .common_utils import process_import_common
from .models import ImportLog, ImportLogProduct
from .tasks import async_import_task


class ImportPageView(LoginRequiredMixin, TemplateView):
    """
    Представление для отображения страницы импорта.

    Шаблон берется из настроек TEMPLATES.
    """

    template_name = "imports/import_page.jinja2"

    def get_context_data(self, **kwargs):
        """
        Получение контекстных данных для шаблона страницы импорта.
        """
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        context["import_logs"] = ImportLog.objects.filter(user=current_user).order_by("-timestamp")
        return context


@method_decorator(login_required, name="dispatch")
class ImportDetailsView(LoginRequiredMixin, View):
    """
    Представление для отображения и обработки деталей импорта товаров.

    Шаблон берется из настроек TEMPLATES.
    """

    template_name = "imports/import_details.jinja2"

    def get(self, request, *args, **kwargs):
        """
        Обработка GET-запроса для отображения деталей импорта.
        """
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        """
        Обработка POST-запроса, начало процесса импорта.

        Параметры:
        - importFile: файл для импорта

        Если пользователь аутентифицирован, создается экземпляр ImportLog,
        и вызывается процесс импорта через common_utils.process_import_common.
        В случае успеха, возвращается успешный шаблон, иначе возвращается шаблон с ошибкой.
        """
        try:
            if request.user.is_authenticated:
                file_name = request.FILES.get("importFile")
                user = request.user
                process_import_common(file_name, user.id)
                async_import_task.apply_async((file_name.name, user.id))
                import_log = ImportLog.objects.latest("timestamp")
                imported_products = (
                    ImportLogProduct.objects.filter(import_log=import_log)
                    .select_related("product")
                    .distinct("product")
                )
                successful_imports_count = imported_products.filter(import_log__status="Выполнен").count()
                failed_imports_count = imported_products.filter(import_log__status="Завершён с ошибкой").count()

                template_name = self.template_name

                context = {
                    "import_log": import_log,
                    "imported_products": imported_products,
                    "successful_imports_count": successful_imports_count,
                    "failed_imports_count": failed_imports_count,
                }

                return render(request, template_name, context)
            else:
                return redirect(reverse_lazy("account_login"))
        except Exception as e:
            # Обработка исключения и предоставление необходимого контекста
            error_message = str(e)
            import_log = ImportLog.objects.latest("timestamp")
            imported_products = (
                ImportLogProduct.objects.filter(import_log=import_log).select_related("product").distinct("product")
            )
            successful_imports_count = imported_products.filter(import_log__status="Выполнен").count()
            failed_imports_count = imported_products.filter(import_log__status="Завершён с ошибкой").count()

            context = {
                "import_log": import_log,
                "imported_products": imported_products,
                "successful_imports_count": successful_imports_count,
                "failed_imports_count": failed_imports_count,
                "error_message": error_message,
                "import_complete": False,
            }

            return render(request, self.template_name, context)


class DownloadCSVTemplateView(LoginRequiredMixin, View):
    """
    Представление для скачивания шаблона CSV-файла.

    Attributes:
        docs_dir (str): Путь к директории с документами.
        file_name (str): Имя CSV-файла.
        file_path (str): Полный путь к CSV-файлу.

    Methods:
        get(request, *args, **kwargs): Обработка GET-запроса для скачивания файла.
    """

    def get(self, request, *args, **kwargs):
        """
        Обработка GET-запроса для скачивания файла.

        Parameters:
            request (HttpRequest): Объект запроса.
            *args: Позиционные аргументы.
            **kwargs: Именованные аргументы.

        Returns:
            HttpResponse: HTTP-ответ с содержимым CSV-файла.
        """
        docs_dir = SiteSettings.load().docs_dir
        file_name = "Sheet1.csv"
        file_path = os.path.join(docs_dir, file_name)

        if not os.path.isfile(file_path):
            return HttpResponse(_("Файл не найден!"))

        try:
            with open(file_path, "rb") as file:
                response = HttpResponse(file.read(), content_type="text/csv")
                response["Content-Disposition"] = f'attachment; filename="{file_name}"'
            return response
        except Exception as e:
            logging.error("Error opening file: %s", str(e))
            return HttpResponse(_("Ошибка при открытии файла."))
