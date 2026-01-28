from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"

    def ready(self):
        """Import signals when Django starts"""
        import apps.accounts.signals.user  # noqa: F401
