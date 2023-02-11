from django.db import models

from appartments.models import PersonalAccount
from receipts.models import Receipt
from users.models import User
from utility_services.models import Tariff


class ArrivalStatement(models.Model):
    personal_account = models.ForeignKey(PersonalAccount, on_delete=models.CASCADE)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    receipt = models.OneToOneField(Receipt, on_delete=models.CASCADE)
    summ = models.DecimalField(max_digits=10, decimal_places=2)
    checked = models.BooleanField()
    date = models.DateField()
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE)


class ExpenseStatement(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    summ = models.DecimalField(max_digits=10, decimal_places=2)
    checked = models.BooleanField()
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()


class Item(models.Model):
    ITEM_TYPE = (
        ('arrive', 'приходная'),
        ('expense', 'расходная'),
    )
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=200, choices=ITEM_TYPE)


