from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        import myapp.signals  # Importar señales para asegurarse de que se activen

        try:
            from .models import WarningList  # Importa el modelo dentro del try para evitar errores
            if hasattr(WarningList, 'create_default_warnings'):  # Verifica si la función existe
                WarningList.create_default_warnings()
        except (OperationalError, ProgrammingError):
            # Ocurre si la base de datos aún no está lista o la tabla no existe
            pass
