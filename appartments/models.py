from django.db import models
from users.models import User

# from utility_services.models import Tariff



# Images for class House contents in currents app. It is determined by different resolves in different objects' galleries.
class House(models.Model):
    title = models.CharField(max_length=500, verbose_name='Название дома')
    address = models.CharField(max_length=500, verbose_name='Адресс')
    main_image = models.ImageField(verbose_name='Изображения', upload_to='galery/', blank=True, null=True)
    responsibilities = models.ManyToManyField('users.User', verbose_name='Обязанности', related_name='responsibilities')

    def __str__(self):
        return self.title


class HouseAdditionalImage(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='addition_images')
    image = models.ImageField(verbose_name='Изображения', upload_to='galery/')



class Section(models.Model):
    title = models.CharField(max_length=500)
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='sections')

    def __str__(self):
        return f"{ self.title }"


class Floor(models.Model):
    title = models.CharField(max_length=500)
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='floors')

    def __str__(self):
        return f"{self.title}"
    

class Appartment(models.Model):
    number = models.PositiveSmallIntegerField()
    area = models.DecimalField(max_digits=7, decimal_places=2)
    personal_account = models.OneToOneField('PersonalAccount', on_delete=models.SET_NULL, related_name="appartment_account", null=True, blank=True) #OneToOne
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name="related_appartment")
    sections = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name="related_appartment")
    floor = models.ForeignKey(Floor, on_delete=models.SET_NULL, null=True, blank=True, related_name="related_appartment")
    owner_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="owning")
    tariff = models.ForeignKey('utility_services.Tariff', on_delete=models.SET_NULL, verbose_name='тариф', related_name='appartment_tariff', blank=True, null=True)
    # balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        # return f'{ self.house }: {self.sections}: {self.floor}: {self.number}'
        return f'{self.number}'
    
    def get_model_fields(model):
        return model._meta.fields

    @property
    def get_account_number(self):
         return self.personal_account.number

class PersonalAccount(models.Model):
    PERSONAL_ACCOUNT_STATUS = (
        ('active', 'Активен'),
        ('nonactive', 'Неактивен')
    )
    number = models.CharField(max_length=200)
    status = models.CharField(max_length=200, choices=PERSONAL_ACCOUNT_STATUS)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.number}"
    
    @classmethod
    def get_verbose_status_dict(cls):
        status_verbose_dict = dict((status, verbose_status) for status, verbose_status in cls.PERSONAL_ACCOUNT_STATUS)
        return status_verbose_dict