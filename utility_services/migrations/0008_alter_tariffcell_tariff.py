# Generated by Django 3.2.17 on 2023-04-05 11:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utility_services', '0007_alter_tariffcell_updated_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tariffcell',
            name='tariff',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='utility_services.tariff'),
        ),
    ]
