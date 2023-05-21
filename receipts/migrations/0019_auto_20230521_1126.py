# Generated by Django 3.2.17 on 2023-05-21 11:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0018_auto_20230520_1134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipt',
            name='from_date',
            field=models.DateField(default=datetime.date(2023, 5, 7)),
        ),
        migrations.AlterField(
            model_name='receipt',
            name='to_date',
            field=models.DateField(default=datetime.date(2023, 5, 21)),
        ),
    ]
