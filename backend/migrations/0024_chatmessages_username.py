# Generated by Django 3.2.4 on 2021-07-03 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0023_privatechatroom_remove'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessages',
            name='username',
            field=models.CharField(default=None, max_length=150),
            preserve_default=False,
        ),
    ]