from django.db import models

from appartments.models import Appartment



class Tariff(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    updated_datetime = models.DateTimeField(blank=True, null=True)
    appartments = models.ManyToManyField(Appartment, verbose_name='квартиры', related_name='tariff', related_query_name="tariff_query", blank=True, null=True)

    def __str__(self):
        return self.title


class TariffCell(models.Model):
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE, blank=True, null=True)
    number = models.SmallIntegerField(blank=True, null=True)
    # description = models.TextField()
    updated_datetime = models.DateTimeField(blank=True, null=True)
    utility_service = models.ForeignKey('UtilityService', on_delete=models.SET_NULL, blank=True, null=True)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    curency = models.CharField(max_length=200, default='грн',)

    def __str__(self):
        if self.tariff != None:
            return f"Ячейка тарифа {self.id}: тариф {self.tariff.title}"
        else:
            return f"Ячейка тарифа {self.id}: тариф не обозначен"


class UtilityService(models.Model):
    title = models.CharField(max_length=200)
    unit_of_measure = models.ForeignKey('UnitOfMeasure', on_delete=models.SET_NULL, blank=True, null=True)
    appartment = models.ForeignKey(Appartment, on_delete=models.SET_NULL, blank=True, null=True)
    shown_in_counters = models.BooleanField(default=False)

    def __str__(self):
        return self.title



class Counter(models.Model):
    title = models.CharField(max_length=200)
    unit_of_measure = models.ForeignKey('UnitOfMeasure', on_delete=models.SET_NULL, blank=True, null=True)
    appartment = models.ForeignKey(Appartment, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.title}: {self.appartment.house.title}, {self.appartment.number}"


class UnitOfMeasure(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class CounterReadings(models.Model):
    COUNTER_READINGS_STATUS = (
        ('zero', 'Нулевое'),
        ('new', 'Новое'),
        ('taken_into_account', 'Учтено'),
        ('taken_into_account_and_paid', 'Учтено и оплачено'),
    )
    counter = models.ForeignKey(Counter, on_delete=models.SET_NULL, blank=True, null=True, related_name='counter_reading')
    status = models.CharField(max_length=200, choices=COUNTER_READINGS_STATUS)
    date = models.DateField()
    readings = models.DecimalField(max_digits=10, decimal_places=2)

    @classmethod
    def get_verbose_status_dict(cls):
        status_verbose_dict = dict((status, verbose_status) for status, verbose_status in cls.COUNTER_READINGS_STATUS)
        return status_verbose_dict