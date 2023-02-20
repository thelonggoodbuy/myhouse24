from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .managers import CustomUserManager



class User(AbstractBaseUser, PermissionsMixin):
    USERS_STATUS = (
    ('active', 'активен'),
    ('new', 'новый'),
    ('disable', 'отключен'),
    )
    USERS_ROLE = (
    ('director', 'директор'),
    ('manager', 'управляющий'),
    ('accounter', 'бухгалтер'),
    ('electrician', 'электри'),
    ('plumber', 'сантехник'),
    ('locksmith', 'слесарь'),
    )
    username = None
    status = models.CharField(max_length=200, choices=USERS_STATUS, null=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    surname = models.CharField(max_length=200, null=True)
    name = models.CharField(max_length=200, null=True)
    patronymic = models.CharField(max_length=200, null=True)
    burn = models.DateField(null=True)
    note = models.TextField(null=True)
    phone = models.CharField(max_length=200, null=True)
    viber = models.CharField(max_length=200, null=True)
    telegam = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=200, unique=True)
    password = models.CharField(max_length=200, blank=True)
    image = models.ImageField(blank=True, null=True, verbose_name='Аватар', upload_to='galery/')
    role = models.CharField(max_length=200, choices=USERS_ROLE, blank=True, null=True)

    # username = None
    USERNAME_FIELD = 'email'
    
    # EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def get_full_name(self):
        return f"{self.surname} {self.name} {self.patronymic}"


class MessageToUser(models.Model):
    topic = models.CharField(max_length=500)
    text = models.TextField()
    date_time = models.DateTimeField()
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="from_user")
    to_users = models.ManyToManyField(User, related_name="to_users")