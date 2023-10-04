# Generated by Django 4.2.5 on 2023-10-04 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='category',
            field=models.CharField(choices=[('N', 'None'), ('B', 'Blue'), ('G', 'Green'), ('O', 'Orange'), ('P', 'Purple'), ('R', 'Red'), ('Y', 'Yellow')], default='N', max_length=1),
        ),
    ]