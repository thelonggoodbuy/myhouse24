# Generated by Django 3.2.17 on 2023-06-12 11:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0025_auto_20230607_1012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipt',
            name='from_date',
            field=models.DateField(default=datetime.date(2023, 5, 29)),
        ),
        migrations.AlterField(
            model_name='receipt',
            name='to_date',
            field=models.DateField(default=datetime.date(2023, 6, 12)),
        ),
    ]