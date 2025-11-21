#!/bin/bash
set -e

echo "Current directory: $(pwd)"
echo "Listing files: $(ls -la)"
echo "Environment variables (excluding SECRET_KEY):"
env | grep -v SECRET_KEY

# Try to collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "Static file collection failed but continuing..."

# Start gunicorn
echo "Starting gunicorn..."
exec gunicorn honestdb_project.wsgi:application --bind 0.0.0.0:8080 --workers 2 --log-level debug
