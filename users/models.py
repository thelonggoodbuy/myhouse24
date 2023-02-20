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
    ('electrician', 'электри'),
    ('plumber', 'сантехник'),
    ('locksmith', 'слесарь'),
    )
    username = None
    status = models.CharField(max_length=200, choices=USERS_STATUS, null=True)
    is_active = models.BooleanField(default=False)
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