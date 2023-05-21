# Generated by Django 3.2.17 on 2023-05-20 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masters_services', '0002_mastersrequest_master'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mastersrequest',
            name='master_type',
            field=models.CharField(choices=[('electrician', 'электрик'), ('plumber', 'сантехник'), ('locksmith', 'слесарь'), ('any_specialist', 'любой специалист')], max_length=200),
        ),
    ]
