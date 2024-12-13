from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        try:
            from .models import WarningList
            WarningList.create_default_warnings()
        except (OperationalError, ProgrammingError):
            # La tabla aún no existe porque las migraciones no se han aplicado
            pass