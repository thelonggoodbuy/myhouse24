from django.db import models

from appartments.models import PersonalAccount
from receipts.models import Receipt
from users.models import User
from utility_services.models import Tariff
from datetime import date
from django.utils import timezone


class Statement(models.Model):

    TYPE_OF_STATEMENT_CHOICES = (
        ('arrival', 'Приход'),
        ('expense', 'Расход'),
    )

    number = models.PositiveBigIntegerField(unique=True)
    date = models.DateField(default=timezone.now())
    # checked_status = models.BooleanField()
    type_of_paynent_item  = models.ForeignKey('PaymentItem', on_delete=models.SET_NULL, null=True, blank=True)
    personal_account = models.ForeignKey(PersonalAccount, on_delete=models.SET_NULL, null=True, blank=True)
    type_of_statement = models.CharField(max_length=200, choices=TYPE_OF_STATEMENT_CHOICES)
    receipt = models.ForeignKey(Receipt, on_delete=models.SET_NULL, null=True, blank=True)
    summ = models.DecimalField(max_digits=10, decimal_places=2)
    checked = models.BooleanField()
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True)
    comment = models.TextField(blank=True, null=True)


    

# class ArrivalStatement(models.Model):
#     personal_account = models.ForeignKey(PersonalAccount, on_delete=models.SET_NULL)
#     item = models.ForeignKey('Item', on_delete=models.SET_NULL)
#     receipt = models.OneToOneField(Receipt, on_delete=models.SET_NULL)
#     summ = models.DecimalField(max_digits=10, decimal_places=2)
#     checked = models.BooleanField()
#     date = models.DateField()
#     manager = models.ForeignKey(User, on_delete=models.SET_NULL)
#     tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL)


# class ExpenseStatement(models.Model):
#     item = models.ForeignKey('Item', on_delete=models.SET_NULL)
#     summ = models.DecimalField(max_digits=10, decimal_places=2)
#     checked = models.BooleanField()
#     manager = models.ForeignKey(User, on_delete=models.SET_NULL)
#     comment = models.TextField()




class PaymentItem(models.Model):
    ITEM_TYPE = (
        ('arrive', 'приходная'),
        ('expense', 'расходная'),
    )
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=200, choices=ITEM_TYPE)

    def __str__(self):
        return self.title