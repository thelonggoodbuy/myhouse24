# Generated by Django 3.2.17 on 2023-05-23 09:23

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('statements', '0016_alter_statement_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statement',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 5, 23, 9, 23, 37, 480678, tzinfo=utc)),
        ),
    ]
