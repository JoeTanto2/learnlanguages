# Generated by Django 3.2.4 on 2021-07-04 00:04

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('backend', '0027_alter_chat_participants'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='participants',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
