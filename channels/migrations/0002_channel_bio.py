# Generated by Django 3.1 on 2020-08-31 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channels', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
    ]