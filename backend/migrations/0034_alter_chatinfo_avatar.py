# Generated by Django 3.2.4 on 2021-07-12 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0033_chatinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatinfo',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='chat_avatar/'),
        ),
    ]
