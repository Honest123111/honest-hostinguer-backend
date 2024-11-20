# celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Configurar el entorno Django para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'honestdb_project.settings')

# Crear la aplicación Celery
app = Celery('honestdb_project')

# Usar la configuración de Django (que contiene la configuración de Celery)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Cargar tareas de todos los módulos registrados de Django
app.autodiscover_tasks()

# Programar tareas periódicas en Celery Beat
app.conf.beat_schedule = {
    'extract-emails-every-5-seconds': {
        'task': 'myapp.tasks.extract_emails_task',  # Nombre de la tarea
        'schedule': 60.0,  # Ejecutar cada 5 segundos
    },
}

@app.task(bind=True)
def debug_task(self):
    print('Debug task executed!')
