from django.db import models
from users.models import User


class House(models.Model):
    title = models.CharField(max_length=500)
    address = models.CharField(max_length=500)
    main_image = models.ImageField(blank=True, verbose_name='Изображения', upload_to='galery/')


class Section(models.Model):
    title = models.CharField(max_length=500)
    main_image = models.ImageField(blank=True, verbose_name='Изображения', upload_to='galery/')
    house = models.ForeignKey(House, on_delete=models.CASCADE)


class Floor(models.Model):
    title = models.CharField(max_length=500)
    main_image = models.ImageField(blank=True, verbose_name='Изображения', upload_to='galery/')
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    sections = models.ForeignKey(Section, on_delete=models.CASCADE)
    

class Appartment(models.Model):
    number = models.PositiveSmallIntegerField()
    area = models.DecimalField(max_digits=7, decimal_places=2)
    personal_account = models.OneToOneField('PersonalAccount', on_delete=models.CASCADE, related_name="personal_account")
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    sections = models.ForeignKey(Section, on_delete=models.CASCADE)
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE)
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)


class PersonalAccount(models.Model):
    PERSONAL_ACCOUNT_STATUS = (
        ('active', 'Активен'),
        ('nonactive', 'Неактивен')
    )
    number = models.CharField(max_length=200)
    status = models.CharField(max_length=200, choices=PERSONAL_ACCOUNT_STATUS)
    appartment = models.OneToOneField(Appartment, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)