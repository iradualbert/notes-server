# Generated by Django 3.1 on 2020-09-03 17:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('channels', '0005_answer_branch_channeladmin_question_review_subscription'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='branch',
            unique_together={('channel', 'main_channel')},
        ),
    ]
