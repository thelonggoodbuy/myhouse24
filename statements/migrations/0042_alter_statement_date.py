# Generated by Django 3.2.17 on 2023-06-12 11:04

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('statements', '0041_alter_statement_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statement',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 6, 12, 11, 3, 59, 828834, tzinfo=utc)),
        ),
    ]