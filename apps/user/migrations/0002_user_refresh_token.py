# Generated by Django 4.1 on 2022-08-22 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="refresh_token",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
