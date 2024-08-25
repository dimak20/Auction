from itertools import repeat

from django.apps import AppConfig


class TenderingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tendering'


    def ready(self):
        from .tasks import close_expired_lots
        close_expired_lots(repeat=300)
