FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system deps required to compile extensions (psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev python3-dev libssl-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and upgrade pip/build tools first
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the application code
COPY . /app

# Ensure Django settings is set (so collectstatic won't fail at build)
ENV DJANGO_SETTINGS_MODULE=honestdb_project.settings
ENV PORT=8080

# Collect static files at build (guarded so build won't fail if settings need runtime secrets)
RUN python manage.py collectstatic --noinput || true

# Informational
EXPOSE 8080

# Start Gunicorn using shell form so $PORT expands at runtime.
CMD ["bash", "-lc", "gunicorn honestdb_project.wsgi:application --bind 0.0.0.0:$PORT --workers 2"]
