from django.shortcuts import render
from django.db.models import F, Q, CharField, Value, Sum
import operator
from functools import reduce
from datetime import datetime, date
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models.functions import Concat
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, JsonResponse
from babel.dates import format_date
import calendar
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import FileResponse
from django.http import HttpResponse
from django.urls import reverse
from general_statistics.models import GraphTotalStatistic
from django.utils.encoding import smart_str
from django.template.loader import render_to_string
from io import BytesIO, StringIO
from django.template.loader import get_template
from general_statistics.models import GraphTotalStatistic
from .services import return_pdf_receipt, return_xlm_receipt
from .forms import ReceiptCellForm
from django import forms
import random
from users.views import RolePassesTestMixin


from decimal import Decimal
from django.contrib.messages.views import SuccessMessageMixin



from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView, DeleteView
from users.models import User
from appartments.models import House, Section, Appartment, PersonalAccount
from utility_services.models import Tariff, TariffCell, CounterReadings
from .models import Receipt, ReceiptCell, Requisite, ReceiptTemplate
from .forms import AddReceiptForm, UtilityReceiptForm, ReceiptCellFormset, RequisiteUpdateForm,\
                     ReceiptTemplateListForm, ReceiptTeplateEditeFormSet, ReceiptTeplateEditeForm 



class CRMReportView(TemplateView):
    
    template_name = "receipts/crm_report.html"



class ReceiptListView(RolePassesTestMixin, TemplateView):
    needfull_permission = 'receipt_permission'
    needfull_user_status = 'is_staff'

    template_name = 'receipts/receipt_list.html'

    def get(self, request, *args, **kwargs):


        # SELECT2 logic
        if self.request.is_ajax() and self.request.GET.get('issue_marker') == 'owners':
            if self.request.GET.get('search'):
                search_data = self.request.GET.get('search')
                owners_data = list(User.objects.filter(full_name__icontains=search_data).values('id', 'full_name'))
                for owner_dict in owners_data: owner_dict['text'] = owner_dict.pop('full_name')
                data = {'results': owners_data}
                return JsonResponse(data)
                

        # users search using Select2
        if self.request.is_ajax() and self.request.GET.get('issue_marker') == 'all_owners':
            owners_data = list(User.objects.all().values('id', 'full_name'))
            for owner_dict in owners_data: owner_dict['text'] = owner_dict.pop('full_name')
            data = {'results': owners_data}
            return JsonResponse(data)



       # datatables serverside logic
        if self.request.is_ajax() and self.request.method == 'GET' and request.GET.get('draw'):
            receipt_data_get_request = request.GET

            #search logic 
            Q_list = []

            # number filtering
            if request.GET.get('columns[1][search][value]'):
                Q_list.append(Q(number__icontains=request.GET.get('columns[1][search][value]')))

            # status filtering
            if request.GET.get('columns[2][search][value]'):
                print(request.GET.get('columns[2][search][value]'))
                if request.GET.get('columns[2][search][value]') != 'all_status':
                    Q_list.append(Q(status=request.GET.get('columns[2][search][value]')))

            # date range search
            if request.GET.get('columns[3][search][value]'):

                date_list = request.GET.get('columns[3][search][value]').split('-')

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
                Q_list.append(Q(to_date__gte=formated_date_start))
                Q_list.append(Q(to_date__lte=formated_date_finish))

            # date with month and year
            if request.GET.get('columns[4][search][value]'):
                date_list = request.GET.get('columns[4][search][value]').split('.')
                month = int(date_list[0])
                year = int(date_list[1])
                first_last_day = calendar.monthrange(year, month)
                first_day = date(year, month, 1)
                last_day = date(year, month, first_last_day[1])
                Q_list.append(Q(date_with_month_year__gte=first_day))
                Q_list.append(Q(date_with_month_year__lte=last_day))

            # full address filter
            if request.GET.get('columns[5][search][value]'):
                search_address_list_parameter = list((request.GET.get('columns[5][search][value]').strip()).split(" "))
                Q_list.append(reduce(operator.and_, (Q(appartments_address__icontains=part_addr) for part_addr in search_address_list_parameter)))

            # full name of owner
            if request.GET.get('columns[6][search][value]'):
                if request.GET.get('columns[6][search][value]'):
                    print(request.GET.get('columns[6][search][value]'))
                    user = User.objects.get(id=request.GET.get('columns[6][search][value]'))
                    Q_list.append(Q(appartment__owner_user=user))


            # payment status filter
            if request.GET.get('columns[7][search][value]'):
                if request.GET.get('columns[7][search][value]') != 'all_payment_status':
                    Q_list.append(Q(payment_was_made=request.GET.get('columns[7][search][value]')))



            draw = int(receipt_data_get_request.get("draw"))
            start = int(receipt_data_get_request.get("start"))
            length = int(receipt_data_get_request.get("length"))



            if receipt_data_get_request.get('order[0][column]') != '':
                number_column = receipt_data_get_request.get('order[0][column]')
                order_column_task = receipt_data_get_request.get(f'columns[{number_column}][name]')
                if receipt_data_get_request.get('order[0][dir]') == 'desc':
                    order_column_task = f"-{order_column_task}"

            if order_column_task == '': order_column_task = '-id'

            raw_data = Receipt.objects.annotate(appartments_address = ArrayAgg(Concat(F('appartment__number'),
                                                                                    Value(', '),
                                                                                    F('appartment__house__title'),
                                                                                    output_field=CharField())
                                                                                    ,distinct=True))\
                                    .annotate(date_with_month_year = F('to_date'))\
                                    .filter(*Q_list)\
                                    .order_by(order_column_task)\
                                    .values('number', 'status', 'to_date',\
                                            'date_with_month_year', 'appartments_address',\
                                            'appartment__owner_user__full_name',\
                                            'payment_was_made', 'total_sum', "id")

            data = list(raw_data)
            verbose_status_dict = Receipt.get_verbose_status_dict()

            for receipt in data:  
                verbose_status = ""
                try: 
                    verbose_status = verbose_status_dict[receipt['status']]
                    receipt['status'] = verbose_status
                except:
                    receipt['status'] = ''


                simple_date = receipt['to_date']
                new_simple_date = format_date(simple_date, 'dd.MM.yyyy', locale='ru')
                receipt['to_date'] = new_simple_date

                date_per_month = receipt['date_with_month_year']
                new_date = format_date(date_per_month, 'LLLL Y', locale='ru')
                receipt['date_with_month_year'] = new_date

                payment_status = receipt['payment_was_made']
                if payment_status == True:
                    receipt['payment_was_made'] = 'Проведена'
                else:
                    receipt['payment_was_made'] = 'Не проведена'



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
        
    def post(self, request, **kwargs):
        if request.POST.get('ajax_indicator') == 'delete_receipt':
            receipt_list = request.POST.getlist('delete_list[]')
            delete_set = Receipt.objects.filter(pk__in=receipt_list)
            general_statistics_object = GraphTotalStatistic.objects.first()
            for receipt in delete_set:

                if (receipt.status == "paid_for" or receipt.status == "partly") \
                    and receipt.payment_was_made == True:
                    general_statistics_object.total_balance -= receipt.total_sum
                    general_statistics_object.total_fund_state -= receipt.total_sum
                    receipt.appartment.personal_account.balance -= receipt.total_sum
                    receipt.appartment.personal_account.save()
                    general_statistics_object.total_debt = -(PersonalAccount.objects.filter(balance__lte=0)\
                                                        .aggregate(Sum('balance'))['balance__sum'])
                receipt.delete()

            general_statistics_object.save()

        response = 'You finished deleteting!'
        return JsonResponse(response, safe=False)



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['general_statistics'] = GraphTotalStatistic.objects.first()

        return context


class AddReceiptView(RolePassesTestMixin, TemplateView):
    needfull_permission = 'receipt_permission'
    needfull_user_status = 'is_staff'
    
    template_name = 'receipts/receipt_create.html'    
    form_class = AddReceiptForm
    model = Receipt
    success_url = reverse_lazy('receipts:receipt_list')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_form'] = AddReceiptForm(prefix='main_form')
        context['utility_form'] = UtilityReceiptForm(prefix='utility_form')
        context['receipt_cell_formset'] = ReceiptCellFormset(prefix='receipt_cell_formset')
        
        return context


    def get(self, request, *args, **kwargs):
        if self.request.is_ajax() and self.request.method == 'GET' and request.GET.get('draw'):
            receipt_data_get_request = request.GET
            Q_list = []
            if request.GET.get('search[value]'):
                if request.GET.get('search[value]') != "empty_appartment":
                    Q_list.append(Q(appartment__id=request.GET.get('search[value]')))

            draw = int(receipt_data_get_request.get("draw"))
            start = int(receipt_data_get_request.get("start"))
            length = int(receipt_data_get_request.get("length"))

            raw_data = CounterReadings.objects.filter(*Q_list)\
                                    .annotate(date_with_month_year = F('date'))\
                                    .values('number', 'status', 'date',\
                                            'date_with_month_year', 'appartment__house__title',\
                                            'appartment__sections__title', 'appartment__number',\
                                            'utility_service__title', 'readings',\
                                            'utility_service__unit_of_measure__title')
            

            data = list(raw_data)
            
            verbose_status_dict = CounterReadings.get_verbose_status_dict()

            for counter_receipt in data:  
                verbose_status = ""
                try: 
                    verbose_status = verbose_status_dict[counter_receipt['status']]
                    counter_receipt['status'] = verbose_status
                except:
                    counter_receipt['status'] = ''


                simple_date = counter_receipt['date']
                new_simple_date = format_date(simple_date, 'dd.MM.yyyy', locale='ru')
                counter_receipt['date'] = new_simple_date

                date_per_month = counter_receipt['date_with_month_year']
                date_per_month = format_date(date_per_month, 'LLLL Y', locale='ru')
                counter_receipt['date_with_month_year'] = date_per_month

            
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
        

        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('ajax_indicator') == 'get_certain_house':
            house_id = self.request.GET['current_house_number']
            house = House.objects.get(id=house_id)
            sections = list(Section.objects.only('id', 'title').filter(house=house).values('id', 'title'))
            appartments = list(Appartment.objects.only('id', 'number').filter(house=house).values('id', 'number'))
            response = {'sections': sections,
                        'appartments':appartments}
            return JsonResponse(response, safe=False)


        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('ajax_indicator') == 'get_appartments_per_sections':
            sections_id = self.request.GET.get('current_sections_number')
            choosen_sections = Section.objects.get(id=sections_id)
            appartments = list(Appartment.objects.only('id', 'number').filter(sections=choosen_sections).values('id', 'number'))
            response = {'appartments':appartments}
            return JsonResponse(response, safe=False)


        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('ajax_indicator') == 'get_personal_account_per_appartment':
            if self.request.GET.get('appartment') != "empty_appartment":
                appartment_id = self.request.GET.get('appartment')
                choosen_personal_account = list(PersonalAccount.objects.filter(appartment_account__id=appartment_id)\
                                                .values('id', 'number', 'appartment_account__owner_user__full_name',\
                                                        'appartment_account__owner_user__id','appartment_account__owner_user__phone'))
                choosen_tariff = list(Tariff.objects.filter(appartment_tariff__id=appartment_id).values('id'))
                response = {'personal_account': choosen_personal_account,
                            'choosen_tariff': choosen_tariff}
                return JsonResponse(response, safe=False)
        

        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('ajax_indicator') == 'add_counters_readings':
            Q_list = []
            tariff_id = self.request.GET.get('tariff_id')
            appartment_id = self.request.GET.get('appartment_data')
            Q_list.append(Q(tariff__id=tariff_id))
            Q_list.append(Q(tariff__appartment_tariff=appartment_id))
            existed_counters_readings = list(CounterReadings.objects.filter(appartment__id=appartment_id).values('utility_service__id').distinct())
            existed_counters = []
            for counter_marker in  existed_counters_readings: existed_counters.append(counter_marker['utility_service__id'])
            Q_list.append(reduce(operator.or_, (Q(utility_service__id=counter_number) for counter_number in existed_counters)))

            tariff_cell_data = list(TariffCell.objects.filter(*Q_list)\
                                            .values('utility_service__id', 'utility_service__unit_of_measure__id', 'cost_per_unit'))
            response = {'tariff_cell_data': tariff_cell_data}
            return JsonResponse(response, safe=False)


        if self.request.is_ajax() and self.request.method == 'GET' and self.request.GET.get('ajax_indicator') == 'add_all_utilities_using_tariff':
            tariff_id = self.request.GET.get('tariff_id')
            counter_tariff_cell_data = list(TariffCell.objects.filter(tariff__id=tariff_id).values('utility_service__id', 'utility_service__unit_of_measure__id', 'cost_per_unit'))
            response = {'counter_tariff_cell_data': counter_tariff_cell_data}
            return JsonResponse(response, safe=False)

        else:
            return super().get(request, *args, **kwargs)


    def post(self, request, *args, **Kwargs):
        main_form = AddReceiptForm(request.POST, prefix='main_form')        
        receipt_cell_formset = ReceiptCellFormset(request.POST, prefix='receipt_cell_formset')
        if main_form.is_valid() and receipt_cell_formset.is_valid():
            return self.form_valid(main_form, receipt_cell_formset)
        else:

            if main_form.errors:
                for field, error in main_form.errors.items():
                    print(f'{field}: {error}')

            if receipt_cell_formset.errors:
                for receipt_form in receipt_cell_formset:
                    for field, error in receipt_form.errors.items():
                        print(f'{field}: {error}')

        
    def form_valid(self, main_form, receipt_cell_formset):
        mainform_instance = main_form.save()
        for receipt_cell_form in receipt_cell_formset:
            receipt_cell = receipt_cell_form.save(commit=False)
            receipt_cell.receipt = mainform_instance
            receipt_cell.save()

        if mainform_instance.payment_was_made == True:
            total_statistic_state = GraphTotalStatistic.objects.first()
            mainform_instance.appartment.personal_account.balance -= mainform_instance.total_sum
            mainform_instance.appartment.personal_account.save()
            total_statistic_state.total_balance -= mainform_instance.total_sum
            total_statistic_state.total_fund_state += mainform_instance.total_sum
            if mainform_instance.appartment.personal_account.balance < 0:
                total_statistic_state.total_debt = -(PersonalAccount.objects.filter(balance__lte=0)\
                                                     .aggregate(Sum('balance'))['balance__sum'])
                total_statistic_state.save()

        
        success_url = self.success_url
        messages.success(self.request, f"Квитанция создана!")
        return HttpResponseRedirect(success_url)
    



class ReceiptCopyView(AddReceiptView):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        receipt_instance = Receipt.objects.get(id=self.kwargs['pk'])
        initial_list_of_dictionary = []
        for receipt_cell in receipt_instance.receipt_cells.all():
            init_dict = {}
            init_dict['utility_service'] = receipt_cell.utility_service
            init_dict['consumption'] = receipt_cell.consumption
            init_dict['unit_of_measure'] = receipt_cell.unit_of_measure
            init_dict['cost_per_unit'] = receipt_cell.cost_per_unit
            init_dict['cost'] = receipt_cell.cost
            initial_list_of_dictionary.append(init_dict)

        receipt_instance.pk = None
        # receipt_instance.number = None
        receipt_instance.number = random.randint(10000000000 , 99999999999)
        while Receipt.objects.filter(number=receipt_instance.number):
            receipt_instance.number = random.randint(10000000000 , 99999999999)

        context['main_form'] = AddReceiptForm(instance=receipt_instance, prefix='main_form')
        initial_object = receipt_instance.appartment
        initial_utility_form_dict = {"house": initial_object.house,
                                    "section": initial_object.sections,
                                    "personal_account": initial_object.personal_account}
        context['utility_form'] = UtilityReceiptForm(initial=initial_utility_form_dict, prefix='utility_form')
        
        CopyReceiptCellFormset = forms.inlineformset_factory(Receipt, ReceiptCell,
                                                        form=ReceiptCellForm, 
                                                        can_delete=True, 
                                                        extra=len(initial_list_of_dictionary), 
                                                        )  


        context['receipt_cell_formset'] = CopyReceiptCellFormset(initial = initial_list_of_dictionary, prefix='receipt_cell_formset')
        
        return context
        


class ReceiptUpdateView(RolePassesTestMixin, UpdateView):
    needfull_permission = 'receipt_permission'
    needfull_user_status = 'is_staff'
    template_name = 'receipts/receipt_create.html'    
    form_class = AddReceiptForm
    model = Receipt
    success_url = reverse_lazy('receipts:receipt_list')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_form'] = AddReceiptForm(instance=self.get_object(), prefix='main_form')
        initial_object = self.get_object().appartment
        initial_utility_form_dict = {"house": initial_object.house,
                                     "section": initial_object.sections,
                                     "personal_account": initial_object.personal_account}
        context['utility_form'] = UtilityReceiptForm(initial=initial_utility_form_dict, prefix='utility_form')
        context['receipt_cell_formset'] = ReceiptCellFormset(instance = self.get_object(), prefix='receipt_cell_formset')
        
        return context


    def post(self, request, *args, **Kwargs):
        main_form = AddReceiptForm(request.POST, instance=self.get_object(), prefix='main_form')        
        receipt_cell_formset = ReceiptCellFormset(request.POST, instance = self.get_object(), prefix='receipt_cell_formset')
        if main_form.is_valid() and receipt_cell_formset.is_valid():
            return self.form_valid(main_form, receipt_cell_formset)
        else:
            if main_form.errors:
                for field, error in main_form.errors.items():
                    print(f'{field}: {error}')

            if receipt_cell_formset.errors:
                for receipt_form in receipt_cell_formset:
                    for field, error in receipt_form.errors.items():
                        print(f'{field}: {error}')

        
    def form_valid(self, main_form, receipt_cell_formset):
        initial_receipt_state = self.get_object()
        mainform_instance = main_form.save()
        for receipt_cell_form in receipt_cell_formset:
            receipt_cell = receipt_cell_form.save(commit=False)
            receipt_cell.receipt = mainform_instance
            receipt_cell.save()

        total_statistic_state = GraphTotalStatistic.objects.first()

        if 'payment_was_made' not in main_form.changed_data\
                    and mainform_instance.payment_was_made == True\
                    and mainform_instance.status == "paid_for": #was +, is +
            # personal account
            mainform_instance.appartment.personal_account.balance -= (mainform_instance.total_sum - initial_receipt_state.total_sum)
            mainform_instance.appartment.personal_account.save()
            # total_statistic_state
            total_statistic_state.total_balance -= (mainform_instance.total_sum - initial_receipt_state.total_sum)
            total_statistic_state.total_fund_state += (mainform_instance.total_sum - initial_receipt_state.total_sum)

        if 'payment_was_made' in main_form.changed_data\
                    and mainform_instance.payment_was_made == False\
                    and mainform_instance.status == "paid_for": #was +, is -
            # personal account
            mainform_instance.appartment.personal_account.balance += initial_receipt_state.total_sum
            mainform_instance.appartment.personal_account.save()
            total_statistic_state.total_balance += initial_receipt_state.total_sum
            total_statistic_state.total_fund_state -= initial_receipt_state.total_sum

        if 'payment_was_made' in main_form.changed_data\
                    and mainform_instance.payment_was_made == True\
                    and mainform_instance.status == "paid_for": #was -, is +
            mainform_instance.appartment.personal_account.balance -= mainform_instance.total_sum
            mainform_instance.appartment.personal_account.save()
            total_statistic_state.total_balance -= mainform_instance.total_sum
            total_statistic_state.total_fund_state += mainform_instance.total_sum

        total_statistic_state.total_debt = -(PersonalAccount.objects.filter(balance__lte=0)\
                                                .aggregate(Sum('balance'))['balance__sum'])
        total_statistic_state.save()

    
        success_url = self.success_url
        messages.success(self.request, f"Квитанция изменена!")
        return HttpResponseRedirect(success_url)


   


class ReceiptDeleteView(RolePassesTestMixin, DeleteView):
    needfull_permission = 'receipt_permission'
    needfull_user_status = 'is_staff'
    model = Receipt
    success_url = reverse_lazy('receipts:receipt_list')
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        receipt_number = self.object.number
        success_url = self.get_success_url()
        if self.object.status == "paid_for" and self.object.payment_was_made == True:
            general_statistics_object = GraphTotalStatistic.objects.first()
            general_statistics_object.total_balance -= self.object.total_sum
            general_statistics_object.total_fund_state -= self.object.total_sum
            self.object.appartment.personal_account.balance -= self.object.total_sum
            self.object.appartment.personal_account.save()
            general_statistics_object.total_debt = -(PersonalAccount.objects.filter(balance__lte=0)\
                                                .aggregate(Sum('balance'))['balance__sum'])
            general_statistics_object.save()

        self.object.delete()
        messages.success(request, (f'Квитанция {receipt_number}. Удалена. Данные о квитанции также удалены'))
        return HttpResponseRedirect(success_url)






class ReceiptCardView(RolePassesTestMixin, DetailView):
    needfull_permission = 'receipt_permission'
    needfull_user_status = 'is_staff'
    queryset = Receipt.objects.all()
    template_name = "receipts/receipt_card.html"
    context_object_name = 'receipt'
    



class ReceiptTemplateListView(RolePassesTestMixin, FormView):
    needfull_permission = 'receipt_permission'
    needfull_user_status = 'is_staff'
    form_class = ReceiptTemplateListForm
    template_name = "receipts/receipt_template_list.html"

    def form_valid(self, form):
        receipt_id = self.kwargs['pk']
        template_id = form.cleaned_data['templates_list']

        if 'print_xls_doc' in self.request.POST:
            response = return_xlm_receipt(receipt_id, template_id)
            # return response

        elif 'send_to_email_pdf' in self.request.POST:
            return_pdf_receipt(receipt_id, template_id)
            response = HttpResponseRedirect(reverse('receipts:receipt_template_list_view', kwargs={'pk': receipt_id}))
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)     
        receipt_id = self.kwargs['pk']
        context['receipt_id'] = receipt_id
        return context
    



class ReceiptTemplateEditeView(RolePassesTestMixin, FormView):
    needfull_permission = 'receipt_permission'
    needfull_user_status = 'is_staff'
    template_name = "receipts/receipt_template_edite.html"
    templates = ReceiptTemplate.objects.all()
    form_class = ReceiptTeplateEditeForm
    success_url = reverse_lazy('receipts:receipt_template_edite_view')


    def post(self, request, *args, **Kwargs):
        template_edit_formset = ReceiptTeplateEditeFormSet(request.POST,\
                                                           request.FILES,\
                                                            queryset=self.templates,\
                                                            prefix="templates")
        
        if template_edit_formset.is_valid():
            return self.form_valid(template_edit_formset)
        else:
            if template_edit_formset.errors:
                for receipt_form in template_edit_formset:
                    for field, error in receipt_form.errors.items():
                        print(f'{field}: {error}')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)     
        context['receipt_edit_formset'] = ReceiptTeplateEditeFormSet(queryset=self.templates,\
                                                                    prefix="templates")
        return context
    

    def form_valid(self, template_edit_formset):
        template_edit_formset.save()
        success_url = self.success_url
        messages.success(self.request, f"Изменения в шаблоны внесены!")
        return HttpResponseRedirect(success_url)
    





    # requiside logic
class RequisiteUpdateView(RolePassesTestMixin, FormView):
    needfull_permission = 'requisite_sections_permission'
    needfull_user_status = 'is_staff'
    model = Requisite
    template_name = "receipts/requiside_update.html"
    form_class = RequisiteUpdateForm
    success_url = reverse_lazy('receipts:receipt_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)     
        context['requisite_form'] = RequisiteUpdateForm(instance=Requisite.objects.first(), prefix="requisite")
        return context
    

    def post(self, request, *args, **Kwargs):
        requisite_form = RequisiteUpdateForm(request.POST, instance=Requisite.objects.first(), prefix="requisite")
        if requisite_form.is_valid():
            return self.form_valid(requisite_form)
        else:
            if requisite_form.errors:
                # for receipt_form in requisite_form:
                for field, error in requisite_form.errors.items():
                    print(f'{field}: {error}')


    def form_valid(self, requisite_form):
        requisite_form.save()
        success_url = self.success_url
        messages.success(self.request, f"Изменения реквизиты внесены!")
        return HttpResponseRedirect(success_url)