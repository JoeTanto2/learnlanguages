# Generated by Django 3.2.4 on 2021-06-29 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0010_alter_user_info_user_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chatmessages',
            old_name='participant',
            new_name='sent_from',
        ),
        migrations.AddField(
            model_name='chatmessages',
            name='sent_to',
            field=models.IntegerField(null=True),
        ),
    ]
