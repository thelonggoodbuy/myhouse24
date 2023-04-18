# Generated by Django 3.2.17 on 2023-04-18 09:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utility_services', '0015_remove_tariff_appartments'),
        ('appartments', '0012_alter_appartment_personal_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='appartment',
            name='tariff',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appartment_tariff', to='utility_services.tariff', verbose_name='тариф'),
        ),
    ]
