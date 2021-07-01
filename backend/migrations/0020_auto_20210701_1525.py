# Generated by Django 3.2.4 on 2021-07-01 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0019_auto_20210701_1521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='chat_name',
            field=models.CharField(blank=True, default=None, max_length=150, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='chat',
            name='is_private',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='chat',
            name='language',
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
    ]