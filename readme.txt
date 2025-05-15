# HonestDB Project

Este repositorio contiene el backend Django de Honest Transportation, configurado para ejecutar tareas asíncronas y programadas usando Celery y Redis.

---

## 🛠️ Requisitos previos

* **Python 3.7+**
* **Git**
* **Redis** (instalado y en ejecución en tu máquina o servidor)
* **Google Cloud y Gmail**

  * API Keys y credenciales de servicio
* **Entorno virtual** (recomendado)

---

## ⚙️ Configuración del entorno

1. **Clona el repositorio**

   ```bash
   git clone git@gitlab.com:daniela1612022/honestdb_project.git
   cd honestdb_project
   ```

2. **Crea y activa un entorno virtual**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instala las dependencias**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Variables de entorno**
   Crea un archivo `.env` en la raíz del proyecto con al menos las siguientes variables (ajusta los valores según tu entorno):

   ```ini
   # Django
   DJANGO_SECRET_KEY=tu_secret_key
   DJANGO_DEBUG=True

   # Base de datos
   DATABASE_URL=postgres://usuario:password@host:puerto/dbname

   # Redis / Celery
   REDIS_URL=redis://localhost:6379/0

   # Google Cloud
   GOOGLE_CLOUD_PROJECT_ID=tu_proyecto
   GOOGLE_CLOUD_CREDENTIALS=/ruta/a/credentials.json

   # Gmail (envío de correos)
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=tu_email@gmail.com
   EMAIL_HOST_PASSWORD=tu_app_password
   EMAIL_USE_TLS=True
   ```

---

## 🔧 Ajustes en `settings.py`

Dentro de `honestdb_project/settings.py` encontrarás:

```python
# Preconfiguración de Celery y Redis
CELERY_BROKER_URL = os.getenv('REDIS_URL')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL')

# Configuración de correo
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
EMAIL_HOST    = os.getenv('EMAIL_HOST')
EMAIL_PORT    = int(os.getenv('EMAIL_PORT', 587))
EMAIL_HOST_USER     = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS       = os.getenv('EMAIL_USE_TLS') == 'True'
```

Revisa y ajusta estas variables según tus servicios de Google Cloud y Gmail.

---

## 🌐 Configuración de Frontend y App Nativa

1. **Dominio y URLs del frontend**

   * Actualiza el dominio del frontend en las variables de entorno o configuración de reverse proxy.
   * Asegúrate de otorgar acceso a las nuevas direcciones, hosting e IPs de los servidores donde estará desplegado el frontend.

2. **Aplicación móvil nativa**

   * Si existe una app nativa (iOS/Android), incluye los mismos cambios de dominio y configuración de API en su archivo de configuración.
   * Verifica que el hosting y las IPs del servidor de backend estén permitidos en los CORS y las reglas de firewall de la app.

---

## ▶️ Ejecutar la aplicación y los workers

1. **Arrancar Redis**

   ```bash
   redis-server
   ```

   En otra terminal, verifica:

   ```bash
   redis-cli ping  # debe responder PONG
   ```

2. **Migraciones y datos iniciales**

   ```bash
   python manage.py migrate
   python manage.py loaddata initial_data.json  # si aplica
   ```

3. **Iniciar el servidor de desarrollo**

   ```bash
   python manage.py runserver
   ```

4. **Iniciar el worker de Celery**

   ```bash
   celery -A honestdb_project worker --loglevel=info
   ```

5. **Iniciar Celery Beat (tareas programadas)**

   ```bash
   celery -A honestdb_project beat --loglevel=info
   ```

---

## 📖 Documentación adicional

* **Celery:** [https://docs.celeryproject.org/](https://docs.celeryproject.org/)
* **Redis:** [https://redis.io/documentation](https://redis.io/documentation)
* **Django-Celery-Beat:** [https://github.com/celery/django-celery-beat](https://github.com/celery/django-celery-beat)

---

## 🤝 Contribuciones

1. Haz un fork de este repositorio.
2. Crea una rama nueva (`git checkout -b feature/mi-feature`).
3. Realiza tus cambios y commitea (`git commit -m "Descripción de mi feature"`).
4. Empuja tu rama (`git push origin feature/mi-feature`).
5. Abre un merge request desde GitLab.

---

## © Derechos de Autor

Aventura Technology y Honest Transportation pueden desarrollarse y mantener el código de forma independiente y sin restricciones, permitiendo a cada parte implementar mejoras, correcciones y nuevas funcionalidades autonomamente.

---

¡Gracias por colaborar! 🚀
