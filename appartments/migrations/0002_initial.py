# Generated by Django 3.2.17 on 2023-02-21 07:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('appartments', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='appartment',
            name='owner_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='appartment',
            name='personal_account',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='personal_account', to='appartments.personalaccount'),
        ),
        migrations.AddField(
            model_name='appartment',
            name='sections',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appartments.section'),
        ),
    ]
