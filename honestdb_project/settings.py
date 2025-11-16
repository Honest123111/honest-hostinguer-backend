from pathlib import Path
from datetime import timedelta
import os
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent



# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent



# Seguridad
SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DEBUG', default='False') == 'True'
AUTH_USER_MODEL = 'myapp.CarrierUser'



# Hosts permitidos (cambia esto con el dominio de tu VPS si tienes uno)
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'srv728671',
    '93.127.215.173',
    'honest-transportation.site',
    'www.honest-transportation.site',
]

# Configuración de la base de datos PostgreSQL en el VPS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'honestdb',
        'USER': 'honestuser',
        'PASSWORD': 'honestpass',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'myapp',
    'django_celery_beat',
    'django_extensions',
    'django_celery_results',
]

# Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # MUST be first
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuración de CORS (Para que el frontend pueda acceder al backend)
# CORS Configuration for Firebase
CORS_ALLOWED_ORIGINS = [
    "https://honesttransportationfron-21ca5.firebaseapp.com",
    "https://honesttransportationfron-21ca5.web.app",
    "http://localhost:3000",
    "http://localhost:5173",
]]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:4200',
    'https://honesttransportationfront.web.app',
    'https://honest-transportation.site',  
]

# Configuración de Redis para Celery y caché
REDIS_URL = 'redis://localhost:6379'
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Configuración de JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Configuración de archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'




# Configuración de archivos multimedia (si necesitas subir archivos)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuración de sesiones con Redis
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Configuración de Celery Beat (si necesitas ejecutar tareas programadas)
CELERY_BEAT_SCHEDULE = {
    'extract-emails-every-minute': {
        'task': 'myapp.tasks.extract_emails_task',
        'schedule': 60.0,  # Ejecutar cada 60 segundos
    },
}

# Configuración de URLs y WSGI
ROOT_URLCONF = 'honestdb_project.urls'
WSGI_APPLICATION = 'honestdb_project.wsgi.application'

# Configuración de validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalización
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Carpeta de plantillas
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 📌 Configuración de Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
    'rest_framework.permissions.AllowAny',
]
}

#CORS_ALLOW_ALL_ORIGINS = True  # 🚀 Permite todas las conexiones temporalmente (solo para desarrollo)
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB máximo

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = "Kevin@honesttransportation.comm" #
EMAIL_HOST_PASSWORD = "Honest123s"

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
FRONTEND_RESET_URL = "https://honesttransportationfron-21ca5.web.app/forgot-password"  # aqui pueden poner la url de su frontend y tambien acceso de su hosting para el reset password



