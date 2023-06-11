# Generated by Django 3.2.17 on 2023-05-23 09:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('masters_services', '0005_rename_desctiption_mastersrequest_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mastersrequest',
            name='master',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='masters_request', to=settings.AUTH_USER_MODEL),
        ),
    ]