from django.shortcuts import render
from django.db.models import Count
from django.views.generic.base import TemplateView


from appartments.models import House, Appartment, PersonalAccount
from users.models import User
from masters_services.models import MastersRequest
from .models import GraphTotalStatistic
from receipts.models import Receipt
from statements.models import Statement
import calendar


from datetime import date
from django.db.models import Q


class GeneralStatisticsView(TemplateView):
    template_name = "general_statistics/general_statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        first_date = date(date.today().year, 1, 1)
        last_date = date(date.today().year, 12, 31)

        all_receipts_list = list(Receipt.objects.filter(Q(from_date__gt=first_date) and Q(from_date__lt=last_date))\
                                            .values("from_date", "total_sum", "status", "payment_was_made"))
        
        recieipt_stat_dict = {}
        for month in (list(calendar.month_name))[1:]:
            recieipt_stat_dict[month] = {'total_debd':0, 'total_payed':0}

        for receipt in all_receipts_list:
            receipt_month = receipt['from_date'].strftime("%B")
            recieipt_stat_dict[receipt_month]['total_debd'] += receipt["total_sum"]
            if receipt['payment_was_made'] == True and receipt['status'] == 'paid_for':
                recieipt_stat_dict[receipt_month]['total_payed'] += receipt["total_sum"]

        all_statemtnts_list = list(Statement.objects.filter(Q(date__gt=first_date)\
                                                            and Q(date__lt=last_date)\
                                                            and Q(checked=True))\
                                                    .values("date", "summ",\
                                                            "type_of_statement"))
        statement_stat_dict = {}
        for month in (list(calendar.month_name))[1:]:
            statement_stat_dict[month] = {'arrival':0, 'expense':0}
        for statement in all_statemtnts_list:
            statement_month = statement['date'].strftime("%B")
            if statement['type_of_statement'] == "arrival":
                statement_stat_dict[statement_month]['arrival'] += statement['summ']
            elif statement['type_of_statement'] == "expense":
                statement_stat_dict[statement_month]['expense'] += statement['summ']

        context['house_quantity'] = House.objects.all().count()
        context['total_users_quantity'] = User.objects.filter(status='active').count()
        context['master_request_in_work_quantity'] = MastersRequest.objects.filter(status='is_performing').count()
        context['appartments_quantity'] = Appartment.objects.all().count()
        context['personal_account_quantity'] = PersonalAccount.objects.all().count()
        context['master_request_new_quantity'] = MastersRequest.objects.filter(status='new').count()
        context['total_statistics'] = GraphTotalStatistic.objects.first()
        context['receipt_statistics_per_month'] = recieipt_stat_dict
        context['statement_stat_dict'] = statement_stat_dict

        return context