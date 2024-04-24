"""
Модуль для обработки задач импорта.
"""

from typing import Optional

from celery import shared_task
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.utils.translation import gettext as _

from .common_utils import process_import_common, create_import_log


@transaction.atomic
def process_import(file_name: str, user_id: int) -> None:
    """
    Задача для обработки импорта продукции из CSV-файла.

    Args:
        file_name (str): Имя загруженного CSV-файла.
        user_id (int): Идентификатор пользователя, загрузившего файл.

    Raises:
        IntegrityError or Exception: В случае ошибки при выполнении транзакции.

    """
    try:
        with transaction.atomic():
            import_log = create_import_log(
                file_name,
                user_id,
                "В процессе выполнения",
            )
            process_import_common(file_name, user_id, import_log)
    except (IntegrityError, Exception) as e:
        create_import_log(file_name, user_id, "Завершён с ошибкой", error_details=str(e))
        raise


@shared_task(ignore_result=False)
def async_import_task(file_name: Optional[str] = None, user_id: Optional[int] = None) -> None:
    """
    Задача для асинхронного выполнения импорта продукции из CSV-файла.

    Args:
        file_name (Optional[str]): Имя загруженного CSV-файла.
        user_id (Optional[int]): Идентификатор пользователя, загрузившего файл.

    Returns:
        None

    """
    if file_name is None or user_id is None:
        return

    task_key = f"async_import_task:{file_name}:{user_id}"  # noqa
    lock_key = f"async_import_lock:{file_name}:{user_id}"

    lock_acquired = cache.add(lock_key, "locked", timeout=60)

    if not lock_acquired:
        print(
            _("Задача уже в очереди для файла: {file_name}, пользователя: {user_id}").format(
                file_name=file_name, user_id=user_id
            )
        )
        return

    print(
        _("Постановка задачи async_import_task для файла: {file_name}, пользователя: {user_id}").format(
            file_name=file_name, user_id=user_id
        )
    )

    try:
        process_import(file_name, user_id)
    except Exception as e:
        print(_("Ошибка в async_import_task: {error}").format(error=e))
    finally:
        cache.delete(lock_key)
