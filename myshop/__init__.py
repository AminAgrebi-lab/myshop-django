# Import the Celery app so it is loaded as soon as Django starts.
# This allows @shared_task to bind to it automatically.
from .celery import app as celery_app

__all__ = ['celery_app']