# Generated by Django 3.2.17 on 2023-04-11 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appartments', '0012_alter_appartment_personal_account'),
        ('utility_services', '0011_alter_counterreadings_counter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tariff',
            name='appartments',
            field=models.ManyToManyField(blank=True, null=True, related_name='tariff', related_query_name='tariff_query', to='appartments.Appartment', verbose_name='квартиры'),
        ),
    ]