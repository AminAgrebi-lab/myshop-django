import os
from celery import Celery

# Set the default Django settings module for the 'celery' CLI program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')

# Create the Celery application instance for this project
app = Celery('myshop')

# Load config from Django settings;
# namespace='CELERY' means settings must be prefixed with 'CELERY_'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks.py modules in all INSTALLED_APPS
app.autodiscover_tasks()