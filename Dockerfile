FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev python3-dev libssl-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Make port 8080 available
EXPOSE 8080

# Set environment variable for Django
ENV PORT=8080
ENV DJANGO_SETTINGS_MODULE=honestdb_project.settings

# Run gunicorn
CMD exec gunicorn honestdb_project.wsgi:application --bind 0.0.0.0:$PORT --workers 2
