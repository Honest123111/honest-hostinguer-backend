web: gunicorn honestdb_project.wsgi
worker: celery -A honestdb_project worker --loglevel=info
beat: celery -A honestdb_project beat --loglevel=info 