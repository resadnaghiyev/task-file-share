from django.db.models.signals import post_save
from django.conf import settings
from .models import Profile


User = settings.AUTH_USER_MODEL


def user_did_save(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


post_save.connect(user_did_save, sender=User)
