from django.db import models

from appartments.models import Appartment, PersonalAccount
from utility_services.models import UtilityService, CounterReadings, Tariff

class Receipt(models.Model):
    RECEIPT_STATUS = (
        ('paid_for', 'Оплачена'),
        ('partly', 'Частично'),
        ('unpaid', 'Неоплачена'),
    )
    status = models.CharField(max_length=200, choices=RECEIPT_STATUS)
    from_data = models.TextField()
    to_data = models.TextField()
    personal_account = models.ForeignKey(PersonalAccount, on_delete=models.CASCADE)
    payment_due = models.DateField()
    total_sum = models.DecimalField(max_digits=10, decimal_places=2)
    appartment = models.ForeignKey(Appartment, on_delete=models.CASCADE)
    payment_was_made = models.BooleanField(default=False)
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE)



class ReceiptCell(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    utility_service = models.ForeignKey(UtilityService, on_delete=models.CASCADE)
    counter_readings = models.OneToOneField(CounterReadings, on_delete=models.CASCADE)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)


class ReceiptTemplate(models.Model):
    name = models.CharField(max_length=200)
    receipt_template = models.FileField(upload_to='mailing_templates/', blank=True)


class Requisite(models.Model):
    company_title = models.CharField(max_length=200)
    description = models.TextField()
