# Generated by Django 5.0.7 on 2024-12-23 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webhook", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="mobile_no",
            field=models.CharField(max_length=12, null=True),
        ),
    ]
