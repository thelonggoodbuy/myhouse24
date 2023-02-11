from django.db import models

from appartments.models import Appartment



class Tariff(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    updated_datetime = models.DateTimeField()


class TariffCell(models.Model):
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE)
    number = models.SmallIntegerField()
    description = models.TextField()
    updated_datetime = models.DateTimeField()
    utility_service = models.ForeignKey('UtilityService', on_delete=models.CASCADE)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    curency = models.CharField(max_length=200)


class UtilityService(models.Model):
    title = models.CharField(max_length=200)
    unit_of_measure = models.ForeignKey('UnitOfMeasure', on_delete=models.CASCADE)
    appartment = models.ForeignKey(Appartment, on_delete=models.CASCADE)



class Counter(models.Model):
    title = models.CharField(max_length=200)
    unit_of_measure = models.ForeignKey('UnitOfMeasure', on_delete=models.CASCADE)
    appartment = models.ForeignKey(Appartment, on_delete=models.CASCADE)


class UnitOfMeasure(models.Model):
    title = models.CharField(max_length=200)


class CounterReadings(models.Model):
    COUNTER_READINGS_STATUS = (
        ('zero', 'Нулевое'),
        ('new', 'Новое'),
        ('taken_into_account', 'Учтено'),
        ('taken_into_account_and_paid', 'Учтено и оплачено'),
    )
    counter = models.ForeignKey(Counter, on_delete=models.CASCADE)
    status = models.CharField(max_length=200, choices=COUNTER_READINGS_STATUS)
    date = models.DateField()
    readings = models.DecimalField(max_digits=10, decimal_places=2)
