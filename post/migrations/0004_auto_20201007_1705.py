# Generated by Django 3.1.1 on 2020-10-07 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0003_subreddit_member_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subreddit',
            name='member_count',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
    ]
