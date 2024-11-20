from django.core.management.base import BaseCommand
from myapp.utils import fetch_and_create_load


class Command(BaseCommand):
    help = "Fetch emails with 'NEW LOAD' and create loads in the database."

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando proceso de extracción de correos...")
        try:
            fetch_and_create_load()
            self.stdout.write(self.style.SUCCESS("Proceso completado con éxito."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error durante el proceso: {e}"))
