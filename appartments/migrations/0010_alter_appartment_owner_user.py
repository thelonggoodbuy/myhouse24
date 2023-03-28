# Generated by Django 3.2.17 on 2023-03-21 11:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appartments', '0009_auto_20230317_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appartment',
            name='owner_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owning', to=settings.AUTH_USER_MODEL),
        ),
    ]
