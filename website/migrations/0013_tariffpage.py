# Generated by Django 3.2.17 on 2023-05-28 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0012_alter_slideblock_target'),
    ]

    operations = [
        migrations.CreateModel(
            name='TariffPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
            ],
        ),
    ]