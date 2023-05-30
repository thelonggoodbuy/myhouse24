from django.db import models

from appartments.models import Appartment
from utility_services.models import UtilityService




class SumPerAppartment(models.Model):
    appartment = models.ForeignKey(Appartment, on_delete=models.CASCADE)
    total_balance = models.DecimalField(max_digits=10, decimal_places=2)
    average_consumption = models.DecimalField(max_digits=10, decimal_places=2)


class PreviousMounthExchangeCell(models.Model):
    appartment = models.ForeignKey(Appartment, on_delete=models.CASCADE)
    utility_service = models.ForeignKey(UtilityService, on_delete=models.CASCADE)
    previous_month_sum = models.DecimalField(max_digits=10, decimal_places=2)


class ExchangePerMounthThisYearCell(models.Model):
    appartment = models.ForeignKey(Appartment, on_delete=models.CASCADE)
    month = models.DecimalField(max_digits=10, decimal_places=2)
    exchange_per_month_sum = models.DecimalField(max_digits=10, decimal_places=2)

# -----------------------------------------------
class CurrentYearExchengeCell(models.Model):
    appartment = models.ForeignKey(Appartment, on_delete=models.CASCADE)
    utility_service = models.ForeignKey(UtilityService, on_delete=models.CASCADE)
    current_year_exchange_summ = models.DecimalField(max_digits=10, decimal_places=2)


class GraphIncomeExpendCell(models.Model):
    month = models.DurationField()
    total_income = models.DecimalField(max_digits=10, decimal_places=2)
    total_expend = models.DecimalField(max_digits=10, decimal_places=2)

# -----------------------------------------------
class GraphPayOffReceiptCell(models.Model):
    month = models.DurationField()
    total_debt = models.DecimalField(max_digits=10, decimal_places=2)
    total_paid_off = models.DecimalField(max_digits=10, decimal_places=2)


class GraphTotalStatistic(models.Model):
    total_debt = models.DecimalField(max_digits=10, decimal_places=2)
    total_balance = models.DecimalField(max_digits=10, decimal_places=2)
    total_fund_state = models.DecimalField(max_digits=10, decimal_places=2)