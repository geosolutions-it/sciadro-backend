# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as api

__all__ = ('api',)
