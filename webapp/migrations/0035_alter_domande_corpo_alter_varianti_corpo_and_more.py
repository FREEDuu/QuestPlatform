# Generated by Django 5.0.1 on 2024-06-04 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0034_remove_domande_webapp_doma_numerop_2e1888_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domande',
            name='corpo',
            field=models.CharField(max_length=400),
        ),
        migrations.AlterField(
            model_name='varianti',
            name='corpo',
            field=models.CharField(max_length=400),
        ),
        migrations.AlterField(
            model_name='varianti',
            name='rispostaEsatta',
            field=models.CharField(default='', max_length=200),
        ),
    ]
