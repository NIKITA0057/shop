# pylint: disable=C0103
""" Модуль для определения URL-путей приложения imports """
from django.urls import path

from .views import ImportPageView, ImportDetailsView, DownloadCSVTemplateView

app_name = "imports"

urlpatterns = [
    path("import/", ImportPageView.as_view(), name="import-page"),
    path("import-details/", ImportDetailsView.as_view(), name="import-details"),
    path("download-csv-template/", DownloadCSVTemplateView.as_view(), name="download-csv-template"),
]
