# Generated by Django 4.2.6 on 2023-10-06 21:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_user_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
    ]
