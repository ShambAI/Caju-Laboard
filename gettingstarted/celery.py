from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gettingstarted.settings')

app = Celery('gettingstarted')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    
}

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

