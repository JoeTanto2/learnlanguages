# Generated by Django 3.2.4 on 2021-07-03 17:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0024_chatmessages_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatmessages',
            name='username',
        ),
    ]
