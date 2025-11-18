# This file is required for Python to recognize this directory as a package

# Use our dummy Celery implementation
from .celery import app as celery_app

__all__ = ('celery_app',)
