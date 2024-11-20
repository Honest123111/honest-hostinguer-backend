Proyecto Django con Celery y Redis

Este proyecto utiliza Celery con Redis para ejecutar tareas asíncronas en segundo plano. A continuación, se explica cómo configurar Redis, Celery y cómo ejecutar el servidor de desarrollo de Django junto con el worker de Celery.

Requisitos previos

Asegúrate de tener lo siguiente instalado en tu sistema:

Python 3.7 o superior
Redis: Instalado en tu máquina
Django: Ya instalado en tu entorno virtual
Celery: Instalado en tu entorno virtual

1. Instalación de Redis

En macOS (con Homebrew)
Si usas macOS y tienes Homebrew, puedes instalar Redis ejecutando:


brew install redis


Instalar las dependencias necesarias
Dentro de tu entorno virtual, instala las siguientes dependencias:

pip install celery
pip install redis
pip install django-celery-beat  # Si necesitas tareas programadas

ABRIR UN TERMINAL POR ITEM
redis-server
(PROBAR REDIS SERVER)
redis-cli ping
DEBE RETORNAR PONG


iniciar celery worker
celery -A honestdb_project worker --loglevel=info
iniciar celery beat
celery -A honestdb_project beat --loglevel=info
correr la DB
python manage.py runserver

