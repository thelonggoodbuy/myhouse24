from django.shortcuts import render
import operator
from functools import reduce

from babel.dates import format_date

from django.views.generic.base import TemplateView
from .models import Statement, PaymentItem, PersonalAccount
from .forms import StatementArrivalCreateForm
from users.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime
from django.urls import reverse_lazy

from django.views.generic.edit import FormView, UpdateView


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

            raw_data = Statement.objects.filter(*Q_list)\
                                .only('number', 'date', 'checked',\
                                    'type_of_paynent_item__title',\
                                    'personal_account__appartment_account__owner_user__full_name',
                                    'personal_account__number', 'type_of_statement', 'summ')\
                                .order_by()\
                                .values('number', 'date', 'checked',\
                                        'type_of_paynent_item__title',\
                                        'personal_account__appartment_account__owner_user__full_name',
                                        'personal_account__number', 'type_of_statement', 'summ', 'id')

            data = list(raw_data)
            print(data)


            # verbose_status_dict = PersonalAccount.get_verbose_status_dict()


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

                # verbose_status = ""
                # try: 
                #     verbose_status = verbose_status_dict[account['status']]
                #     account['status'] = verbose_status
                # except:
                #     account['status'] = ''

                


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


        # select 2 all owners data
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
        
        success_url = self.success_url
        messages.success(self.request, f"Приходская ведомость готова!")
        return HttpResponseRedirect(success_url)
    

class StatementExpenseCreateView(StatementCreateView):

    def form_valid(self, statement_form):
        inst = statement_form.save()
        inst.type_of_statement = 'expense'
        inst.save()
        
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
        statement_form.save()
        success_url = self.success_url
        messages.success(self.request, f"Изменения в ведомость внесены!")
        return HttpResponseRedirect(success_url)