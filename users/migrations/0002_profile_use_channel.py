# Generated by Django 3.1 on 2020-09-03 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='use_channel',
            field=models.BooleanField(default=False),
        ),
    ]
