# Generated by Django 5.0.1 on 2024-02-08 13:06

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0018_testsgroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistiche',
            name='dataOraInserimento',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]