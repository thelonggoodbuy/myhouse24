# Generated by Django 3.2.17 on 2023-04-25 10:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appartments', '0013_appartment_tariff'),
        ('utility_services', '0018_counter_utility_service'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='counterreadings',
            name='counter',
        ),
        migrations.AddField(
            model_name='counterreadings',
            name='utility_service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='counter_reading', to='utility_services.utilityservice'),
        ),
        migrations.AddField(
            model_name='utilityservice',
            name='appartment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='appartments.appartment'),
        ),
        migrations.DeleteModel(
            name='Counter',
        ),
    ]