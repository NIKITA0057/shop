from django.apps import AppConfig


class SettingsAppConfig(AppConfig):
    """Конфигурация приложения настроек."""

    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "settings_app"
