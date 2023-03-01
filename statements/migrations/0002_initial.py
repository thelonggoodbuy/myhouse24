# Generated by Django 3.2.17 on 2023-02-21 07:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('receipts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('utility_services', '0001_initial'),
        ('appartments', '0002_initial'),
        ('statements', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='expensestatement',
            name='manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='arrivalstatement',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='statements.item'),
        ),
        migrations.AddField(
            model_name='arrivalstatement',
            name='manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='arrivalstatement',
            name='personal_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appartments.personalaccount'),
        ),
        migrations.AddField(
            model_name='arrivalstatement',
            name='receipt',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='receipts.receipt'),
        ),
        migrations.AddField(
            model_name='arrivalstatement',
            name='tariff',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='utility_services.tariff'),
        ),
    ]