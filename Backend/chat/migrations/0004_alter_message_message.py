# Generated by Django 5.1.5 on 2025-02-02 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_message_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='message',
            field=models.TextField(blank=True),
        ),
    ]
