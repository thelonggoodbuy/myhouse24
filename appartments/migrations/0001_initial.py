# Generated by Django 3.2.17 on 2023-02-21 07:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appartment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField()),
                ('area', models.DecimalField(decimal_places=2, max_digits=7)),
                ('balance', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='House',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('address', models.CharField(max_length=500)),
                ('main_image', models.ImageField(blank=True, upload_to='galery/', verbose_name='Изображения')),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('main_image', models.ImageField(blank=True, upload_to='galery/', verbose_name='Изображения')),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appartments.house')),
            ],
        ),
        migrations.CreateModel(
            name='PersonalAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=200)),
                ('status', models.CharField(choices=[('active', 'Активен'), ('nonactive', 'Неактивен')], max_length=200)),
                ('balance', models.DecimalField(decimal_places=2, max_digits=10)),
                ('appartment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='appartments.appartment')),
            ],
        ),
        migrations.CreateModel(
            name='Floor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('main_image', models.ImageField(blank=True, upload_to='galery/', verbose_name='Изображения')),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appartments.house')),
                ('sections', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appartments.section')),
            ],
        ),
        migrations.AddField(
            model_name='appartment',
            name='floor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appartments.floor'),
        ),
        migrations.AddField(
            model_name='appartment',
            name='house',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appartments.house'),
        ),
    ]
