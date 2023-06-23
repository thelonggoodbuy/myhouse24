# Generated by Django 3.2.17 on 2023-06-23 16:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('status', models.CharField(choices=[('active', 'активен'), ('new', 'новый'), ('disable', 'отключен')], max_length=200, null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('surname', models.CharField(blank=True, max_length=200, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('patronymic', models.CharField(blank=True, max_length=200, null=True)),
                ('full_name', models.CharField(blank=True, max_length=600, null=True)),
                ('burn', models.DateField(blank=True, null=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('phone', models.CharField(blank=True, max_length=200, null=True)),
                ('viber', models.CharField(blank=True, max_length=200, null=True)),
                ('telegram', models.CharField(blank=True, max_length=200, null=True)),
                ('email', models.EmailField(max_length=200, unique=True)),
                ('password', models.CharField(blank=True, max_length=200)),
                ('image', models.ImageField(blank=True, null=True, upload_to='galery/', verbose_name='Аватар')),
                ('email_confirmed', models.BooleanField(default=False)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='название')),
                ('type', models.CharField(max_length=200, null=True)),
                ('statistic_permission', models.BooleanField(default=True, verbose_name='статистика')),
                ('fund_permission', models.BooleanField(default=False, verbose_name='касса')),
                ('receipt_permission', models.BooleanField(default=False, verbose_name='квитанции на оплату')),
                ('accounts_permission', models.BooleanField(default=False, verbose_name='лицевые счета')),
                ('appartments_permission', models.BooleanField(default=False, verbose_name='квартиры')),
                ('owners_permission', models.BooleanField(default=False, verbose_name='владельцы квартир')),
                ('house_permission', models.BooleanField(default=True, verbose_name='дома')),
                ('messages_permission', models.BooleanField(default=False, verbose_name='сообщения')),
                ('masters_request_permission', models.BooleanField(default=True, verbose_name='заявки вызова мастера')),
                ('counter_permission', models.BooleanField(default=False, verbose_name='счетчики')),
                ('site_managing_permission', models.BooleanField(default=False, verbose_name='управление сайтом')),
                ('utility_services_permission', models.BooleanField(default=False, verbose_name='услуги')),
                ('tarif_permission', models.BooleanField(default=False, verbose_name='тарифы')),
                ('role_section_permission', models.BooleanField(default=False, verbose_name='роли')),
                ('users_sections_permission', models.BooleanField(default=False, verbose_name='пользователи')),
                ('requisite_sections_permission', models.BooleanField(default=False, verbose_name='платежные реквизиты')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_confirmed', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MessageToUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=200)),
                ('text', models.TextField()),
                ('date_time', models.DateTimeField()),
                ('message_target_type', models.CharField(choices=[('one_user', 'один пользователь'), ('all_users_per_house', 'по домам'), ('all_users_per_floor', 'по этажам'), ('all_users_per_sections', 'по секциям'), ('all_users', 'все пользователи')], default='all_users', max_length=200)),
                ('from_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='from_user', to=settings.AUTH_USER_MODEL)),
                ('read_by_user', models.ManyToManyField(related_name='readed_by_user', to=settings.AUTH_USER_MODEL)),
                ('to_users', models.ManyToManyField(related_name='to_users', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.role'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
