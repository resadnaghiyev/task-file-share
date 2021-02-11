from fileshare.celery import app
from datetime import datetime, date, timedelta
from django.utils import timezone

from .models import File, Share, Comment


@app.task
def remove_files_after_seven_days():
    seven_days = timezone.now() - timedelta(days=7)
    files = File.objects.filter(uploaded_at__lt=seven_days)
    comments = Comment.objects.filter(timestamp__lt=seven_days)
    files.delete()
    comments.delete()

    for obj in Share.objects.all():
        if obj.shared_file.all().exists() == False:
            obj.delete()
