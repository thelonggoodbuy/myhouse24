# Generated by Django 3.2.17 on 2023-04-14 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appartments', '0012_alter_appartment_personal_account'),
        ('utility_services', '0012_alter_tariff_appartments'),
    ]

    operations = [
        migrations.AddField(
            model_name='counterreadings',
            name='number',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='tariff',
            name='appartments',
            field=models.ManyToManyField(blank=True, null=True, related_name='tariff', to='appartments.Appartment', verbose_name='квартиры'),
        ),
    ]