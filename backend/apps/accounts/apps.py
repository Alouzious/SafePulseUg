from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name               = 'apps.accounts'        # ← must match folder path
    verbose_name       = 'Officer Accounts'