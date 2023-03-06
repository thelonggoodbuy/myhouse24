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
    USERS_ROLE = (
    ('director', 'директор'),
    ('manager', 'управляющий'),
    ('accounter', 'бухгалтер'),
    ('electrician', 'электрик'),
    ('plumber', 'сантехник'),
    ('locksmith', 'слесарь'),
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
    telegam = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(max_length=200, unique=True)
    password = models.CharField(max_length=200, blank=True)
    image = models.ImageField(blank=True, null=True, verbose_name='Аватар', upload_to='galery/')
    role = models.CharField(max_length=200, choices=USERS_ROLE, blank=True, null=True)
    email_confirmed = models.BooleanField(default=False)

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
        return self.email
    
    # get verbouse name for filters in list of users 
    def get_verbose_role(self):
        if self.role != None:
            return dict(User.USERS_ROLE)[self.role]
        else:
            return 'Роль не назначена'
    
    def get_verbose_status(self):
        return dict(User.USERS_STATUS)[self.status]
    
    # get choiches tupples for forms
    @classmethod 
    def get_users_role_tupple(cls):
        return User.USERS_ROLE
    
    @classmethod
    def get_users_status_tupple(cls):
        return User.USERS_STATUS
    
    @classmethod
    def get_verbose_status_dict(cls):
        status_verbose_dict = dict((status, verbose_status) for status, verbose_status in cls.USERS_STATUS)
        return status_verbose_dict

    @classmethod
    def get_verbose_roles_dict(cls):
        role_verbose_dict = dict((role, verbose_role) for role, verbose_role in cls.USERS_ROLE)
        return role_verbose_dict

    def save(self, *args, **kwargs):
        self.full_name = (f"{self.surname} {self.name} {self.patronymic}").strip()
        super(User, self).save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)

    @receiver(post_save, sender=User)
    def update_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
            instance.profile.save()



class MessageToUser(models.Model):
    topic = models.CharField(max_length=500)
    text = models.TextField()
    date_time = models.DateTimeField()
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="from_user")
    to_users = models.ManyToManyField(User, related_name="to_users")