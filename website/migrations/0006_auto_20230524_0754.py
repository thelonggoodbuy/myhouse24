# Generated by Django 3.2.17 on 2023-05-24 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_alter_mainpage_seo_block'),
    ]

    operations = [
        migrations.CreateModel(
            name='document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='document/', verbose_name='Файл')),
                ('target', models.CharField(choices=[('about_us', 'о нас')], max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='aboutuspage',
            name='addition_short_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='aboutuspage',
            name='addition_title',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='aboutuspage',
            name='short_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='aboutuspage',
            name='title',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
