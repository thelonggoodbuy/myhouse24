from django.db import models

from django.contrib.auth.models import AbstractBaseUser, AbstractUser, PermissionsMixin



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
    status = models.CharField(max_length=200, choices=USERS_STATUS)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    surname = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    patronymic = models.CharField(max_length=200)
    burn = models.DateField()
    note = models.TextField()
    phone = models.CharField(max_length=200)
    viber = models.CharField(max_length=200)
    telegam = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, unique=True)
    password = models.CharField(max_length=200, blank=True)
    image = models.ImageField(blank=True, verbose_name='Аватар', upload_to='galery/')
    role = models.CharField(max_length=200, choices=USERS_ROLE, blank=True, null=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    # objects = CustomUserManager()


class MessageToUser(models.Model):
    topic = models.CharField(max_length=500)
    text = models.TextField()
    date_time = models.DateTimeField()
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="from_user")
    to_users = models.ManyToManyField(User, related_name="to_users")