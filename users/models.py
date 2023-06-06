from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.urls import reverse


from .managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    USERS_STATUS = (
    ('active', 'активен'),
    ('new', 'новый'),
    ('disable', 'отключен'),
    )

    username = None
    status = models.CharField(max_length=200, choices=USERS_STATUS, null=True)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    surname = models.CharField(max_length=200, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    patronymic = models.CharField(max_length=200, blank=True, null=True)
    full_name = models.CharField(max_length=600, blank=True, null=True)
    burn = models.DateField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=200, blank=True, null=True)
    viber = models.CharField(max_length=200, blank=True, null=True)
    telegram = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(max_length=200, unique=True)
    password = models.CharField(max_length=200, blank=True)
    image = models.ImageField(blank=True, null=True, verbose_name='Аватар', upload_to='galery/')
    role = models.ForeignKey('Role', on_delete=models.SET_NULL, blank=True, null=True)
    email_confirmed = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    # username = None
    USERNAME_FIELD = 'email'
    
    # EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def get_full_name(self):
        return f"{self.surname} {self.name} {self.patronymic}"

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_absolute_url(self):
         return reverse('users:login_user')

    def __str__(self):
        return self.full_name
    
    def get_verbose_status(self):
        return dict(User.USERS_STATUS)[self.status]
    
    @classmethod
    def get_users_status_tupple(cls):
        return User.USERS_STATUS
    
    @classmethod
    def get_verbose_status_dict(cls):
        status_verbose_dict = dict((status, verbose_status) for status, verbose_status in cls.USERS_STATUS)
        return status_verbose_dict

    

    def save(self, *args, **kwargs):
        self.full_name = (f"{self.surname} {self.name} {self.patronymic}").strip()
        super(User, self).save(*args, **kwargs)

class Role(models.Model):
    name = models.CharField(max_length=200, verbose_name = 'название')
    type = models.CharField(max_length=200, null=True)
    statistic_permission = models.BooleanField(default=True, verbose_name = 'статистика')
    fund_permission = models.BooleanField(default=False, verbose_name = 'касса')
    receipt_permission = models.BooleanField(default=False, verbose_name = 'квитанции на оплату')
    accounts_permission = models.BooleanField(default=False, verbose_name = 'лицевые счета')
    appartments_permission = models.BooleanField(default=False, verbose_name = 'квартиры')
    owners_permission = models.BooleanField(default=False, verbose_name = 'владельцы квартир')
    house_permission = models.BooleanField(default=True, verbose_name = 'дома')
    messages_permission = models.BooleanField(default=False, verbose_name = 'сообщения')
    masters_request_permission = models.BooleanField(default=True, verbose_name = 'заявки вызова мастера')
    counter_permission = models.BooleanField(default=False, verbose_name = 'счетчики')
    site_managing_permission = models.BooleanField(default=False, verbose_name = 'управление сайтом')
    utility_services_permission = models.BooleanField(default=False, verbose_name = 'услуги')
    tarif_permission = models.BooleanField(default=False, verbose_name = 'тарифы')
    role_section_permission = models.BooleanField(default=False, verbose_name = 'роли')
    users_sections_permission = models.BooleanField(default=False, verbose_name = 'пользователи')
    requisite_sections_permission = models.BooleanField(default=False, verbose_name = 'платежные реквизиты')

    def __str__(self):
        return self.name

    def return_permission_is(self, require_perm):
        is_permit = getattr(self, require_perm)
        return is_permit


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)

    @receiver(post_save, sender=User)
    def update_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
            instance.profile.save()



class MessageToUser(models.Model):
    MESSAGE_TARGET = (
    ('one_user', 'один пользователь'),
    ('all_users_per_house', 'по домам'),
    ('all_users_per_floor', 'по этажам'),
    ('all_users_per_sections', 'по секциям'),
    ('all_users', 'все пользователи')
    )
    topic = models.CharField(max_length=200)
    text = models.TextField()
    date_time = models.DateTimeField()
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="from_user", null=True, blank=True)
    to_users = models.ManyToManyField(User, related_name="to_users")
    message_target_type = models.CharField(max_length=200, choices=MESSAGE_TARGET, default='all_users')
    read_by_user = models.ManyToManyField(User, related_name="readed_by_user")