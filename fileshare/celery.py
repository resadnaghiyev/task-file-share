import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fileshare.settings')

app = Celery('fileshare')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'remove_files': {
        'task': 'files.tasks.remove_files_after_seven_days',
        'schedule': crontab(minute=0, hour=0),
    },
}
