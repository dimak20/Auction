from django.apps import AppConfig


class TenderingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tendering"

    def ready(self):
        pass
