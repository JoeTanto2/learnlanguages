# Generated by Django 3.2.4 on 2021-07-01 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0018_alter_chat_chat_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='is_private',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='chat',
            name='language',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]