import os
from celery import Celery

# Set the default settings module for 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medinex.settings')

# Create Celery app with name 'medinex'
app = Celery('medinex')

# Load task settings from Django's settings.py with CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()
