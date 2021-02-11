from django.db import models
from datetime import date
from django.urls import reverse
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver

User = settings.AUTH_USER_MODEL


class File(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="files", verbose_name="İstifadəçi"
    )
    title = models.CharField("Adı", max_length=100)
    myfile = models.FileField(upload_to='files/', blank=False, null=False)
    description = models.CharField("Açıqlaması", max_length=250)
    uploaded_at = models.DateTimeField("Yüklənmə tarixi", auto_now_add=True)

    def __str__(self):
        return f'{self.id} -- {self.title} -- {self.user.username}'


class ShareTime(models.Model):
    shared_file = models.ForeignKey(File, on_delete=models.CASCADE)
    share = models.ForeignKey("Share", on_delete=models.CASCADE)
    is_comment = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shared_file.title}"

    class Meta:
        ordering = ['-timestamp']


class Share(models.Model):
    shared_file = models.ManyToManyField(
        File, blank=True, related_name="shared", verbose_name="File", through=ShareTime
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_comment = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user}'


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id} - {self.user.username}'


class ChatTime(models.Model):
    comments = models.ForeignKey(Comment, on_delete=models.CASCADE)
    chat = models.ForeignKey("Chat", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']


class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name='chats', blank=True)
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='chats')
    comments = models.ManyToManyField(
        Comment, blank=True, related_name="chat", verbose_name="comment", through=ChatTime
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.file.title}"


@receiver(post_delete)
def delete_files_when_row_deleted_from_db(sender, instance, **kwargs):
    for field in sender._meta.concrete_fields:
        if isinstance(field,models.FileField):
            instance_file_field = getattr(instance,field.name)
            delete_file_if_unused(sender,instance,field,instance_file_field)
        
   
def delete_file_if_unused(model,instance,field,instance_file_field):
    dynamic_field = {}
    dynamic_field[field.name] = instance_file_field.name
    other_refs_exist = model.objects.filter(**dynamic_field).exclude(pk=instance.pk).exists()
    if not other_refs_exist:
        instance_file_field.delete(False)
