# Generated by Django 3.2.17 on 2023-04-03 13:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appartments', '0012_alter_appartment_personal_account'),
        ('utility_services', '0002_tariff_appartments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='counter',
            name='appartment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='appartments.appartment'),
        ),
        migrations.AlterField(
            model_name='counter',
            name='unit_of_measure',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='utility_services.unitofmeasure'),
        ),
        migrations.AlterField(
            model_name='counterreadings',
            name='counter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='utility_services.counter'),
        ),
        migrations.AlterField(
            model_name='tariffcell',
            name='tariff',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='utility_services.tariff'),
        ),
        migrations.AlterField(
            model_name='tariffcell',
            name='utility_service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='utility_services.utilityservice'),
        ),
        migrations.AlterField(
            model_name='utilityservice',
            name='appartment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='appartments.appartment'),
        ),
        migrations.AlterField(
            model_name='utilityservice',
            name='unit_of_measure',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='utility_services.unitofmeasure'),
        ),
    ]
