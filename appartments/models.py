from django.db import models
from users.models import User

 



# Images for class House contents in currents app. It is determined by different resolves in different objects' galleries.
class House(models.Model):
    title = models.CharField(max_length=500, verbose_name='Название дома')
    address = models.CharField(max_length=500, verbose_name='Адресс')
    main_image = models.ImageField(verbose_name='Изображения', upload_to='galery/', blank=True, null=True)
    responsibilities = models.ManyToManyField(User, verbose_name='Обязанности', related_name='responsibilities')

    def __str__(self):
        return self.title


class HouseAdditionalImage(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='addition_images')
    image = models.ImageField(verbose_name='Изображения', upload_to='galery/')



class Section(models.Model):
    title = models.CharField(max_length=500)
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='sections')

    def __str__(self):
        return f"{ self.title }: { self.house.title }"


class Floor(models.Model):
    title = models.CharField(max_length=500)
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='floors')

    def __str__(self):
        return f"{self.house.title}: {self.title}"
    

class Appartment(models.Model):
    number = models.PositiveSmallIntegerField()
    area = models.DecimalField(max_digits=7, decimal_places=2)
    personal_account = models.OneToOneField('PersonalAccount', on_delete=models.SET_NULL, related_name="appartment_account", null=True, blank=True)
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    sections = models.ForeignKey(Section, on_delete=models.CASCADE)
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE)
    owner_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="owning")
    # balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{ self.house }: {self.sections}: {self.floor}: {self.number}'
    
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
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.number}"
    
    @classmethod
    def get_verbose_status_dict(cls):
        status_verbose_dict = dict((status, verbose_status) for status, verbose_status in cls.PERSONAL_ACCOUNT_STATUS)
        return status_verbose_dict