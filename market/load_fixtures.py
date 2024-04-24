"""
Модуль для загрузки фикстур в Django.

Этот модуль предоставляет функцию `load_all_fixtures`, которая ищет файлы JSON в каталоге 'fixtures' и загружает их
с использованием команды управления 'loaddata'.

"""
import os
from django.core.management import call_command
from django import setup


def load_all_fixtures():
    """
    Загрузить все фикстуры Django из указанного каталога.

    Этот скрипт ищет файлы JSON в каталоге 'fixtures' и загружает их с использованием команды управления 'loaddata'.

    Использование:
        - Убедитесь, что переменная среды DJANGO_SETTINGS_MODULE установлена на модуль настроек вашего проекта Django.
        - Запустите скрипт с использованием интерпретатора Python.

    Пример:
        python load_fixtures.py
    """

    fixture_dir = "./fixtures"

    for file_name in sorted(os.listdir(fixture_dir)):
        file_path = os.path.join(fixture_dir, file_name)

        # Check if file_name is a file before attempting to load it
        if os.path.isfile(file_path) and file_name.endswith(".json"):
            call_command("loaddata", file_path)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    setup()

    load_all_fixtures()
