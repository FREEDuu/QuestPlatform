# Generated by Django 5.0.1 on 2024-01-20 22:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0002_rename_idtest_test_utenti_test_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Person',
        ),
    ]
