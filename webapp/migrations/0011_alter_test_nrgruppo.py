# Generated by Django 5.0.1 on 2024-01-29 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0010_rename_domanda_test_domande_varianti_iddomanda_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='nrGruppo',
            field=models.IntegerField(default=0),
        ),
    ]
