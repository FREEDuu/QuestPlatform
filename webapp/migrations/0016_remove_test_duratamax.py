# Generated by Django 5.0.1 on 2024-02-01 10:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0015_statistiche_utente'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='test',
            name='durataMax',
        ),
    ]
