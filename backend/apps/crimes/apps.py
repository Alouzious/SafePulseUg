from django.apps import AppConfig


class CrimesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name               = 'apps.crimes'
    verbose_name       = 'Crime Reports'