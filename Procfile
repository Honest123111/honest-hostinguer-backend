release: python manage.py migrate
web: gunicorn honestdb_project.wsgi --log-file -
worker: celery -A honestdb_project worker --loglevel=info
beat: celery -A honestdb_project beat --loglevel=info
