from django.shortcuts import render
import operator
from functools import reduce
import random


from babel.dates import format_date
from django.db.models import Sum
from django.views.generic.base import TemplateView
from .models import Statement, PaymentItem, PersonalAccount
from .forms import StatementArrivalCreateForm, PaymentItemCreateForm
from users.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from general_statistics.models import GraphTotalStatistic
from receipts.services import return_xlm_list_of_statements, return_xlm_statement_data


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime
from django.urls import reverse_lazy
from general_statistics.models import GraphTotalStatistic
from django.views.generic.edit import FormView, UpdateView, CreateView, DeleteView
from django.views.generic.detail import DetailView


# Create your views here.
class StatementListView(TemplateView):
    template_name = 'statements/statement_list.html'

    def get(self, request, *args, **kwargs):

       # datatables serverside logic
        if self.request.is_ajax() and self.request.method == 'GET' and request.GET.get('draw'):
            statement_data_get_request = request.GET
            #search logic 
            Q_list = []

            if request.GET.get('columns[0][search][value]'):
                Q_list.append(Q(number__icontains=request.GET.get('columns[0][search][value]')))


            if request.GET.get('columns[1][search][value]'):

                date_list = request.GET.get('columns[1][search][value]').split('-')

                start_date = date_list[0].strip().split('.')
                finish_date = date_list[1].strip().split('.')
                start_date.reverse()
                finish_date.reverse()

                start_date_string = ''
                finish_date_string = ''
                
                start_date_string = '-'.join(str(elem) for elem in start_date)
                finish_date_string = '-'.join(str(elem) for elem in finish_date)

                formated_date_start = datetime.strptime(start_date_string, '%Y-%m-%d')
                formated_date_finish = datetime.strptime(finish_date_string, '%Y-%m-%d')
                Q_list.append(Q(date__gte=formated_date_start))
                Q_list.append(Q(date__lte=formated_date_finish))


            if request.GET.get('columns[2][search][value]'):
                if request.GET.get('columns[2][search][value]') != 'all_status':
                    Q_list.append(Q(checked=request.GET.get('columns[2][search][value]')))


            if request.GET.get('columns[3][search][value]'):
                if request.GET.get('columns[3][search][value]') != 'all_type_of_items':
                    Q_list.append(Q(type_of_paynent_item__id=request.GET.get('columns[3][search][value]')))


            if request.GET.get('columns[4][search][value]'):
                if request.GET.get('columns[4][search][value]'):
                    Q_list.append(Q(personal_account__appartment_account__owner_user__id=request.GET.get('columns[4][search][value]')))


            if request.GET.get('columns[5][search][value]'):
                Q_list.append(Q(personal_account__number__icontains=request.GET.get('columns[5][search][value]')))


            if request.GET.get('columns[6][search][value]'):
                if request.GET.get('columns[6][search][value]') != 'all_types_of_statements':
                    Q_list.append(Q(type_of_statement=request.GET.get('columns[6][search][value]')))



            draw = int(statement_data_get_request.get("draw"))
            start = int(statement_data_get_request.get("start"))
            length = int(statement_data_get_request.get("length"))


            if statement_data_get_request.get('order[0][column]') != '' or order_column_task != None:
                number_column = statement_data_get_request.get('order[0][column]')
                order_column_task = statement_data_get_request.get(f'columns[{number_column}][name]')
                if statement_data_get_request.get('order[0][dir]') == 'desc':
                    order_column_task = f"-{order_column_task}"

            if order_column_task == '' or order_column_task == None: order_column_task = '-id'

            raw_data = Statement.objects.filter(*Q_list)\
                                .only('number', 'date', 'checked',\
                                    'type_of_paynent_item__title',\
                                    'personal_account__appartment_account__owner_user__full_name',
                                    'personal_account__number', 'type_of_statement', 'summ', 'id')\
                                .order_by(order_column_task)\
                                .values('number', 'date', 'checked',\
                                        'type_of_paynent_item__title',\
                                        'personal_account__appartment_account__owner_user__full_name',
                                        'personal_account__number', 'type_of_statement', 'summ', 'id')

            data = list(raw_data)

            for statement in data:
                simple_date = statement['date']
                new_simple_date = format_date(simple_date, 'dd.MM.yyyy', locale='ru')
                statement['date'] = new_simple_date

                simple_checked = statement['checked']
                if simple_checked == True:
                    statement['checked'] = 'Проведен'
                else:
                    statement['checked'] = 'Не проведен'

                simple_type_of_statement = statement['type_of_statement']
                if simple_type_of_statement == 'arrival':
                    statement['type_of_statement'] = 'Приход'
                else:
                    statement['type_of_statement'] = 'Расход'


            # paginator here
            paginator = Paginator(data, length)
            page_number = start / length + 1
            try:
                obj = paginator.page(page_number).object_list
            except PageNotAnInteger:
                obj = paginator(1).object_list
            except EmptyPage:
                obj = paginator.page(1).object_list

            total = len(data)
            records_filter = total

            response = {
                'data': obj,
                'draw': draw,
                'recordsTotal:': total,
                'recordsFiltered': records_filter,
            }
            return JsonResponse(response, safe=False)

        # # users search using Select2
        if self.request.is_ajax() and self.request.GET.get('issue_marker') == 'all_owners':
            owners_data = list(User.objects.filter(owning__isnull=False).values('id', 'full_name'))
            for owner_dict in owners_data: owner_dict['text'] = owner_dict.pop('full_name')
            data = {'results': owners_data}
            return JsonResponse(data)

        else:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = PaymentItem.objects.all()
        context['general_statistics'] = GraphTotalStatistic.objects.first()
        
        return context
    

class StatementCreateView(FormView):
    template_name = "statements/statement_create.html"
    form_class = StatementArrivalCreateForm
    success_url = reverse_lazy('statements:statements_list')


    def get(self, request, *args, **kwargs):
        
        if self.request.is_ajax() and self.request.GET.get('issue_marker') == 'all_owners':
            owners_data = list(User.objects.filter(owning__isnull=False).values('id', 'full_name'))
            for owner_dict in owners_data: owner_dict['text'] = owner_dict.pop('full_name')
            data = {'results': owners_data}
            return JsonResponse(data)


        # select 2 owners data
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('issue_marker') == 'owner_marker':
            if self.request.GET.get('search'):
                search_data = self.request.GET.get('search')
                owners_Q_list = []
                search_full_name_list_parameter = list((search_data.strip()).split(" "))
                owners_Q_list.append(reduce(operator.and_, (Q(full_name__icontains=part_name) for part_name in search_full_name_list_parameter)))
                owners_Q_list.append(Q(owning__isnull=False))
                owners_data = list(User.objects.filter(*owners_Q_list).distinct().values('id', 'full_name'))
                for owner_dict in owners_data: owner_dict['text'] = owner_dict.pop('full_name')
                data = {'results': owners_data}
                return JsonResponse(data)

        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('issue_marker') == 'all_owners_marker':
            owners_data = list(User.objects.filter(owning__isnull=False).distinct().values('id', 'full_name'))
            for owner_dict in owners_data: owner_dict['text'] = owner_dict.pop('full_name')
            data = {'results': owners_data}
            return JsonResponse(data)

        # select 2 all personal accounts data
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('issue_marker') == 'personal_account':
            # print(self.request.GET)
            Q_accounts_list = []
            if self.request.GET.get('search'):
                search_data = self.request.GET.get('search')
                Q_accounts_list.append(Q(number__icontains=search_data))
                if self.request.GET.get('owner_marker') != '': Q_accounts_list.append(Q(appartment_account__owner_user__id=self.request.GET.get('owner_marker')))
                personal_account_data = list(PersonalAccount.objects.filter(*Q_accounts_list).distinct().values('id', 'number'))
                for owner_dict in personal_account_data: owner_dict['text'] = owner_dict.pop('number')
                data = {'results': personal_account_data}
                return JsonResponse(data)
            
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('issue_marker') == 'all_personal_account':
            # print(self.request.GET)
            Q_accounts_list = []
            if self.request.GET.get('owner_marker') != '': Q_accounts_list.append(Q(appartment_account__owner_user__id=self.request.GET.get('owner_marker')))

            personal_account_data = list(PersonalAccount.objects.filter(*Q_accounts_list).values('id', 'number'))
            for owner_dict in personal_account_data: owner_dict['text'] = owner_dict.pop('number')
            data = {'results': personal_account_data}
            return JsonResponse(data)


        # corelate account with owner
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('issue_marker') == 'correlate_account_with_owner':
            if self.request.GET.get('personal_account') != '':
                user_data = list(User.objects.filter(owning__personal_account__id=self.request.GET.get('personal_account')).values('id'))
                user_id = user_data[0]['id']
                data = {'user_id': user_id}
                return JsonResponse(data)


        # select 2 managers
        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('issue_marker') == 'manager':
            if self.request.GET.get('search'):
                search_data = self.request.GET.get('search')
                owners_Q_list = []
                search_full_name_list_parameter = list((search_data.strip()).split(" "))
                owners_Q_list.append(reduce(operator.and_, (Q(full_name__icontains=part_name) for part_name in search_full_name_list_parameter)))
                owners_Q_list.append(Q(role__isnull=False))
                owners_data = list(User.objects.filter(*owners_Q_list).distinct().values('id', 'full_name', 'role__name'))
                for owner_dict in owners_data: 
                    full_name = owner_dict.pop('full_name')
                    role = owner_dict.pop('role__name')
                    owner_str = f'{role}: {full_name}'
                    owner_dict['text'] = owner_str
                data = {'results': owners_data}
                return JsonResponse(data)

        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('issue_marker') == 'all_managers':
            owners_data = list(User.objects.filter(role__isnull=False).distinct().values('id', 'full_name', 'role__name'))
            for owner_dict in owners_data:
                full_name = owner_dict.pop('full_name')
                role = owner_dict.pop('role__name')
                owner_str = f'{role}: {full_name}'
                owner_dict['text'] = owner_str

            data = {'results': owners_data}
            return JsonResponse(data)



        else:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)



    def post(self, request, *args, **Kwargs):
        statement_form = StatementArrivalCreateForm(request.POST, prefix="statement_form")

        if statement_form.is_valid():

            return self.form_valid(statement_form)
        else:
            if statement_form.errors:
                for field, error in statement_form.errors.items():
                    print(f'{field}: {error}')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)     
        context['statement_form'] = StatementArrivalCreateForm(prefix="statement_form")
        return context


class StatementArrivalCreateView(StatementCreateView):

    def form_valid(self, statement_form):
        inst = statement_form.save()
        inst.type_of_statement = 'arrival'
        inst.save()
        if inst.checked == True:
            # balance logic
            inst.personal_account.balance += inst.summ
            inst.personal_account.save()
            # statistics logic
            total_statistic_state = GraphTotalStatistic.objects.first()
            total_statistic_state.total_fund_state += inst.summ
            total_statistic_state.total_balance += inst.summ
            total_statistic_state.total_debt = -(PersonalAccount.objects.filter(balance__lte=0).aggregate(Sum('balance'))['balance__sum'])
            total_statistic_state.save()
        
        success_url = self.success_url
        messages.success(self.request, f"Приходская ведомость готова!")
        return HttpResponseRedirect(success_url)
    

class StatementExpenseCreateView(StatementCreateView):

    def form_valid(self, statement_form):
        inst = statement_form.save()
        inst.type_of_statement = 'expense'
        inst.save()
        if inst.checked == True:
            # balance logic
            inst.personal_account.balance -= inst.summ
            inst.personal_account.save()
            # statistics logic
            total_statistic_state = GraphTotalStatistic.objects.first()
            total_statistic_state.total_fund_state -= inst.summ
            total_statistic_state.total_balance -= inst.summ
            total_statistic_state.total_debt = -(PersonalAccount.objects.filter(balance__lte=0).aggregate(Sum('balance'))['balance__sum'])
            total_statistic_state.save()


        success_url = self.success_url
        messages.success(self.request, f"Расходная ведомость готова!")
        return HttpResponseRedirect(success_url)
    

class StatementUpdateView(UpdateView):
    template_name = "statements/statement_create.html"
    form_class = StatementArrivalCreateForm
    success_url = reverse_lazy('statements:statements_list')
    model = Statement


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)     
        context['statement_form'] = StatementArrivalCreateForm(instance=self.get_object(), prefix="statement_form")
        return context


    def post(self, request, *args, **Kwargs):
        statement_form = StatementArrivalCreateForm(request.POST, instance=self.get_object(), prefix="statement_form")
        if statement_form.is_valid():
            return self.form_valid(statement_form)
        else:
            if statement_form.errors:
                for field, error in statement_form.errors.items():
                    print(f'{field}: {error}')


    def form_valid(self, statement_form):
        
    # statistic and logic for pretending 
        initial_statement_state = self.get_object()
        inst = statement_form.save(commit=False)
        total_statistic_state = GraphTotalStatistic.objects.first()

    # if we turn on statement
        if 'checked' in statement_form.changed_data and inst.checked == True:

            if initial_statement_state.type_of_statement == "arrival":
                inst.personal_account.balance += inst.summ
                total_statistic_state.total_fund_state += inst.summ
                total_statistic_state.total_balance += inst.summ

            elif initial_statement_state.type_of_statement == "expense":
                inst.personal_account.balance -= inst.summ
                total_statistic_state.total_fund_state -= inst.summ
                total_statistic_state.total_balance -= inst.summ
        
    # if we turn off statement
        elif 'checked' in statement_form.changed_data and inst.checked == False:

            if initial_statement_state.type_of_statement == "arrival":
                inst.personal_account.balance -= initial_statement_state.summ
                total_statistic_state.total_fund_state -= initial_statement_state.summ
                total_statistic_state.total_balance -= initial_statement_state.summ

            elif initial_statement_state.type_of_statement == "expense":
                inst.personal_account.balance += initial_statement_state.summ
                total_statistic_state.total_fund_state += initial_statement_state.summ
                total_statistic_state.total_balance += initial_statement_state.summ

    # changes in general statistics if we change data in statements
        if 'checked' not in statement_form.changed_data and inst.checked == True:
            
            if initial_statement_state.type_of_statement == "arrival":
                inst.personal_account.balance += inst.summ - initial_statement_state.summ
                total_statistic_state.total_fund_state += inst.summ - initial_statement_state.summ
                total_statistic_state.total_balance += inst.summ - initial_statement_state.summ

            elif initial_statement_state.type_of_statement == "expense":
                inst.personal_account.balance -= inst.summ - initial_statement_state.summ
                total_statistic_state.total_fund_state -= inst.summ - initial_statement_state.summ
                total_statistic_state.total_balance -= inst.summ - initial_statement_state.summ

        inst.personal_account.save()
        total_statistic_state.total_debt = -(PersonalAccount.objects.filter(balance__lte=0).aggregate(Sum('balance'))['balance__sum'])
        total_statistic_state.save()


        inst.save()

        success_url = self.success_url
        messages.success(self.request, f"Изменения в ведомость внесены!")
        return HttpResponseRedirect(success_url)



def statemets_print_all(request):
    response = return_xlm_list_of_statements()
    return response


def statemets_print_current_statment(request, pk):
    response = return_xlm_statement_data(pk)
    return response


class StatementDetailView(DetailView):
    queryset = Statement.objects.select_related('personal_account__appartment_account__owner_user', 'type_of_paynent_item', 'manager').all()    
    # model = Statement
    template_name = "statements/statement_detail.html"
    context_object_name = 'statement'



class StatementArrivalCopyView(StatementArrivalCreateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        statement_instance = Statement.objects.get(id=self.kwargs['pk'])
        statement_instance.pk = None
        statement_instance.number = random.randint(10000000000 , 99999999999)
        while Statement.objects.filter(number=statement_instance.number):
            statement_instance.number = random.randint(10000000000 , 99999999999)
        context['statement_form'] = StatementArrivalCreateForm(instance=statement_instance, prefix="statement_form")
        return context



class StatementExpenseCopyView(StatementExpenseCreateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        statement_instance = Statement.objects.get(id=self.kwargs['pk'])
        statement_instance.pk = None
        statement_instance.number = random.randint(10000000000 , 99999999999)
        while Statement.objects.filter(number=statement_instance.number):
            statement_instance.number = random.randint(10000000000 , 99999999999)
        context['statement_form'] = StatementArrivalCreateForm(instance=statement_instance, prefix="statement_form")
        return context



# =====================================================================
# ===================STATEMENT===DELETE================================
# =====================================================================
class ReceiptDeleteView(DeleteView):

    model = Statement
    success_url = reverse_lazy('statements:statements_list')
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        total_statistic = GraphTotalStatistic.objects.first()

        if self.object.checked == True :

            if self.object.type_of_statement == "arrival":
                self.object.personal_account.balance -= self.object.summ
                total_statistic.total_fund_state -= self.object.summ
                total_statistic.total_balance -= self.object.summ


            elif self.object.type_of_statement == "expense":
                self.object.personal_account.balance += self.object.summ
                total_statistic.total_fund_state += self.object.summ
                total_statistic.total_balance += self.object.summ

        self.object.delete()

        messages.success(request, (f'Ведомость. Удалена. Данные о квитанции также удалены'))
        return HttpResponseRedirect(success_url)

# =====================================================================
# ============END====STATEMENT===DELETE================================
# =====================================================================



class PaymentItemList(TemplateView):
    template_name = 'statements/payment_item_list.html'

    def get(self, request, *args, **kwargs):
       # datatables serverside logic
        if self.request.is_ajax() and self.request.method == 'GET' and request.GET.get('draw'):
            account_data_get_request = request.GET
            #search logic 
            Q_list = []
            draw = int(account_data_get_request.get("draw"))
            start = int(account_data_get_request.get("start"))
            length = int(account_data_get_request.get("length"))

            raw_data = PaymentItem.objects.filter(*Q_list)\
                                .only('title', 'type', 'id')\
                                .order_by()\
                                .values('title', 'type', 'id')

            data = list(raw_data)

            for item in data:
                if item['type'] == 'arrive':
                    item['type'] = 'приходная'
                elif item['type'] == 'expense':
                    item['type'] = 'расходная'
                
            print(data)

            # paginator here
            paginator = Paginator(data, length)
            page_number = start / length + 1
            try:
                obj = paginator.page(page_number).object_list
            except PageNotAnInteger:
                obj = paginator(1).object_list
            except EmptyPage:
                obj = paginator.page(1).object_list

            total = len(data)
            records_filter = total

            response = {
                'data': obj,
                'draw': draw,
                'recordsTotal:': total,
                'recordsFiltered': records_filter,
            }
            return JsonResponse(response, safe=False)

        else:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    



class PaymentItemCreateView(CreateView):

    template_name = 'statements/payment_item_create.html'
    form_class = PaymentItemCreateForm
    success_url = reverse_lazy('statements:payment_item_list')


    def post(self, request, *args, **Kwargs):
        item_form = PaymentItemCreateForm(request.POST, prefix="payment_item_form")

        if item_form.is_valid():

            return self.form_valid(item_form)
        else:
            if item_form.errors:
                for field, error in item_form.errors.items():
                    print(f'{field}: {error}')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)     
        context['item_form'] = PaymentItemCreateForm(prefix="payment_item_form")
        return context
    


class PaymentItemUpdateView(UpdateView):

    template_name = 'statements/payment_item_create.html'
    form_class = PaymentItemCreateForm
    model = PaymentItem
    success_url = reverse_lazy('statements:payment_item_list')

    def post(self, request, *args, **Kwargs):
        item_form = PaymentItemCreateForm(request.POST, instance=self.get_object(), prefix="payment_item_form")

        if item_form.is_valid():

            return self.form_valid(item_form)
        else:
            if item_form.errors:
                for field, error in item_form.errors.items():
                    print(f'{field}: {error}')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)     
        context['item_form'] = PaymentItemCreateForm(instance=self.get_object(), prefix="payment_item_form")
        return context
    
class PaymentItemDeleteView(DeleteView):

    model = PaymentItem
    success_url = reverse_lazy('statements:payment_item_list')
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)