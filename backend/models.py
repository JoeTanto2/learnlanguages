from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class User_info (models.Model):
    user_id = models.ForeignKey(User, related_name='info', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    sex = models.CharField(max_length=50, blank=True, null=True)
    about = models.CharField(max_length=500, null=True, blank=True)
    country = models.CharField(max_length=60, null=True, blank=True)
    native = models.CharField(max_length=50)
    desired = models.CharField(max_length=50)

class Chat (models.Model):
    participants = models.ManyToManyField(User, blank=True)
    chat_name = models.CharField(max_length=150, blank=True)

class ChatMessagesManager (models.Manager):
    def messages(self, room):
        text = ChatMessages.objects.filter(room=room).order_by("-timestamp")
        return text


class ChatMessages (models.Model):
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Chat, on_delete=models.CASCADE)
    messages = models.CharField(max_length=500, unique=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    texts = ChatMessagesManager()
