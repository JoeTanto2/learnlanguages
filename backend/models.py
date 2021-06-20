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
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    sex = models.CharField(max_length=50, blank=True)
    about = models.CharField(max_length=500, blank=True)
    country = models.CharField(max_length=60, blank=True)
    native = models.CharField(max_length=50)
    desired = models.CharField(max_length=50)
