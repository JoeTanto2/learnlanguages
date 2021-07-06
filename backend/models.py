import django.contrib.auth.models
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import os
import json
from django.core.serializers.json import DjangoJSONEncoder

model = User
class Meta:
    unique_together = [['username', 'id']]

def natural_key(self):
    return (self.username, self.id)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class User_info (models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    sex = models.CharField(max_length=50, blank=True, null=True)
    about = models.CharField(max_length=500, null=True, blank=True)
    country = models.CharField(max_length=60, null=True, blank=True)
    native = models.CharField(max_length=50)
    desired = models.CharField(max_length=50)

    def __str__(self):
        return ''.join(self.user_id.username)

class Chat (models.Model):
    chat_name = models.CharField(max_length=150, blank=True, unique=True, null=True)
    language = models.CharField(max_length=50, null=True, blank=True)
    participants = models.ManyToManyField(User, blank=True)
    is_private = models.BooleanField(default=False, blank=True)

    objects = models.Manager()
    def __str__(self):
        if self.chat_name:
            return ''.join(self.chat_name)
        else:
            return ''.join(str(self.id))

class PrivateChatRoom (models.Model):
    room = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user', null=True, on_delete=models.SET_NULL)
    user1 = models.ForeignKey(User, related_name='user1', null=True, on_delete=models.SET_NULL)
    private = models.BooleanField(default=True)
    remove = models.BooleanField(default=False)

class ChatRoom (models.Model):
    chat_id = models.OneToOneField(Chat, on_delete=models.CASCADE)
    users = models.ManyToManyField(User, blank=True, related_name='users')

    def __str__(self):
        return ''.join(self.chat_id.chat_name)


class ChatMessagesManager (models.Manager):
    def messages(self, room):
        text = ChatMessages.objects.filter(room=room).order_by("-timestamp")
        return text
    def call (self):
        o = ChatMessages.natural_key(self)


class ChatMessages (models.Model):
    room = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sent_from = models.ForeignKey(User, on_delete=models.CASCADE)
    sent_to = models.IntegerField(null=True, blank=True)
    messages = models.CharField(max_length=500, unique=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    texts = ChatMessagesManager()
    objects = models.Manager()

    def __str__(self):
        return ''.join(self.sent_from.username)

    def natural_key(self):
        return (self.sent_from,) + self.sent_from.natural_key()

    natural_key.dependencies = ['django.contrib.auth.models.User']

class ProfilePicture (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='avatar/')

    def __str__(self):
        return f'{self.picture}'


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    # def delete(self, *args, **kwargs):
    #     self.picture.delete(save=False)
    #     super().delete()

@receiver(models.signals.post_delete, sender=ProfilePicture)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.picture:
        instance.picture.delete(save=False)  ## use for aws s3
            # if os.path.isfile(instance.image.path): ## use this in development
            #     os.remove(instance.image.path)

@receiver(models.signals.pre_save, sender=ProfilePicture)
def delete_old_file (sender, instance, **kwargs):
    try:
        old_instance = ProfilePicture.objects.get(id=instance.id)
    except old_instance.DoesNotExist:
        return None
    old_instance.picture.delete(save=False)


